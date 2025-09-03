from os import stat
from .printer import Printer
from . import router
from .message import *
from . import constants
from .input_unit import InputUnit
from .scheduler_thread import SchedulerThread

import time

class TerminalKeyInput():
    """Handles input from a keyboard
    """

    # Change these to whatever you want, high is when pressed, low is when not pressed
    highValue = constants.BUTTON_PRESS
    lowValue = constants.BUTTON_RELEASE

    _scheduler = SchedulerThread()

    _debug = False

    _willSpawnThreads = False

    _clearKeys = {}

    _pressed = set()

    # The keys registered for manual input
    _keys = {}

    _hotkeys = []

    # The keys registered for interrupts
    _keyInterrupts = {}

    # Our keyboard listener, only exists if someone uses 'key_interrupt'
    _listener = None

    _keyHandlers = []

    @staticmethod
    def shouldSpawnThreads(should):
        if should and not TerminalKeyInput._willSpawnThreads:
            print("Starting")
            TerminalKeyInput._scheduler.start()
        elif not should and TerminalKeyInput._willSpawnThreads:
            TerminalKeyInput._scheduler.stop(blockWait=True)
        TerminalKeyInput._willSpawnThreads = should

    @staticmethod
    def setDebug(enable):
        TerminalKeyInput._debug = enable

    @staticmethod
    def scheduleKeyClear():
        for key, time in TerminalKeyInput._clearKeys.items():
            pass
        TerminalKeyInput._scheduler.scheduleItem(1000, TerminalKeyInput.scheduleKeyClear, priority=-1)

    @staticmethod
    def registerKeyHandler(fun):
        TerminalKeyInput._keyHandlers.append(fun)

    @staticmethod
    def removeKeyHandler(fun):
        if fun in TerminalKeyInput._keyHandlers:
            TerminalKeyInput._keyHandlers.remove(fun)

    @staticmethod
    def clearKeys(enable):
        for h in TerminalKeyInput._hotkeys:
            h.clear()
        TerminalKeyInput._pressed.clear()

    @staticmethod
    def initKey(button):
        """ Inits a key to be recognized as valid input

        Args:
            button (Dictionary): Information about a button
        """
        if (button['trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % button['trigger'])
            return False
        TerminalKeyInput._keys[button['trigger']] = "_button_{}".format(button['name'])
        return True

    @staticmethod
    def onPress(key):
        """ Callback for pressing a key

        Args:
            key (Key): A key object defined by pynput
        """

        can = TerminalKeyInput._listener.canonical(key)
        char = key
        if (hasattr(key, 'char')):
            char = key.char

        TerminalKeyInput.handleInterrupt(char, "1")

        for h in TerminalKeyInput._hotkeys:
            h.press(can)

        for handler in TerminalKeyInput._keyHandlers:
            handler(char, constants.BUTTON_PRESS)

        if TerminalKeyInput._debug:
            TerminalKeyInput._pressed.add(can)
            Printer.print(f"Pressed: '{key}'. State: {TerminalKeyInput._pressed}", Printer.DEBUG)

    @staticmethod
    def onRelease(key):
        """ Callback for releasing a key

        Args:
            key (Key): A key object defined by pynput
        """
        # We are not guaranteed a char input, NOTE: Maybe we need to support non char keys?

        can = TerminalKeyInput._listener.canonical(key)
        char = key
        if (hasattr(key, 'char')):
            char = key.char
        TerminalKeyInput.handleInterrupt(char, "0")

        for h in TerminalKeyInput._hotkeys:
            h.release(can)

        for handler in TerminalKeyInput._keyHandlers:
            handler(char, constants.BUTTON_RELEASE)

        if TerminalKeyInput._debug and can in TerminalKeyInput._pressed:
            TerminalKeyInput._pressed.remove(can)
            Printer.print(f"Released: '{key}'. State: {TerminalKeyInput._pressed}", Printer.DEBUG)

    @staticmethod
    def handleInterrupt(keyString, action):
        """ Handles all the interrupt keys

        Args:
            keyString (string): The key pressed
            action ([type]): The event that took place to trigger this, "0" or "1"
        """
        ints = TerminalKeyInput._keyInterrupts
        send = None
        if (keyString in ints):
            val = ints[keyString]
            if ("_button_" in val):
                val = ints[keyString].replace("_button_", "")
                if val == "":
                    val = keyString
                if action == "1":
                    send = constants.BUTTON_PRESS
                elif action == "0":
                    send = constants.BUTTON_RELEASE

            # We only care about up presses for encoders
            # NOTE: This seems really minor and natural, but could be configurable with the json
            elif("_left_" in val and action == "1"):
                val = val.replace("_left_", "")
                if val == "":
                    val = keyString
                send = constants.ENCODER_LEFT
            elif("_right_" in val and action == "1"):
                val = val.replace("_right_", "")
                if val == "":
                    val = keyString
                send = constants.ENCODER_RIGHT
            if send is not None:
                if TerminalKeyInput._scheduler.running:
                    TerminalKeyInput._scheduler.scheduleItem(0, lambda: router.sendMessage(InputCommand(val, send)))
                else:
                    router.sendMessage(InputCommand(val, send))

    @staticmethod
    def createPressFun(key):
        """ Simply calls the normal press interrupt handler

        Args:
            key (string): The hotkey string
        """
        def fun():
            TerminalKeyInput.handleInterrupt(key, constants.BUTTON_PRESS)
        return fun

    @staticmethod
    def createReleaseFun(key):
        """ Simply calls the normal press interrupt handler

        Args:
            key (string): The hotkey string
        """
        def fun():
            TerminalKeyInput.handleInterrupt(key, constants.BUTTON_RELEASE)
        return fun

    @staticmethod
    def startKeyListener():
        from pynput import keyboard
        TerminalKeyInput._listener = keyboard.Listener(
            on_press=TerminalKeyInput.onPress,
            on_release=TerminalKeyInput.onRelease
        )
        TerminalKeyInput._listener.start()

    @staticmethod
    def registerKeyInterrupt(key):
        """ Registers a new interrupt key to report

        Args:
            key (Dictionary): Information about the key
        """
        if (TerminalKeyInput._listener == None):
            TerminalKeyInput.startKeyListener()
        # Make sure we have do not have duplicate keys anywhere:
        if (key['trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring" % key['trigger'])
            return False
        TerminalKeyInput._keyInterrupts[key['trigger']] = "_button_{}".format(key['name'])

        if (len(key['trigger']) > 1):
            from pynput import keyboard
            from .releasable_hotkey import ReleaseableHotkey
            try:
                keys = keyboard.HotKey.parse(key['trigger'])
                for i in range(len(keys)):
                    keys[i] = TerminalKeyInput._listener.canonical(keys[i])
                TerminalKeyInput._hotkeys.append(ReleaseableHotkey(keys, TerminalKeyInput.createPressFun(key['trigger']), TerminalKeyInput.createReleaseFun(key['trigger'])))
            except Exception as e:
                # TODO: Do we want to handle this somehow?
                print("this cannot be added", key, e)
                pass
        return True

    @staticmethod
    def registerEncoderInterrupt(encoder):
        """ Registers a new 'encoder' for

        Args:
            encoder (Dictionary): Info about the encoder
        """
        if (TerminalKeyInput._listener == None):
            TerminalKeyInput.startKeyListener()
        # Make sure we have do not have duplicate keys anywhere:
        if (encoder['left_trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring encoder" % (encoder['left_trigger']))
            return False
        if (encoder['right_trigger'] in TerminalKeyInput._keyInterrupts):
            Printer.print("Duplicate trigger '%s', ignoring encoder" % (encoder['right_trigger']))
            return False

        # TODO: Add hotkey support to this
        TerminalKeyInput._keyInterrupts[encoder['right_trigger']] = "_right_{}".format(encoder['name'])
        TerminalKeyInput._keyInterrupts[encoder['left_trigger']] = "_left_{}".format(encoder['name'])

        if (len(encoder['left_trigger']) > 1):
            from pynput import keyboard
            try:
                keys = keyboard.HotKey.parse(encoder['left_trigger'])
                for i in range(len(keys)):
                    keys[i] = TerminalKeyInput._listener.canonical(keys[i])
                TerminalKeyInput._hotkeys.append(keyboard.HotKey(keys, TerminalKeyInput.createPressFun(encoder['left_trigger'])))
            except Exception as e:
                # TODO: Do we want to handle this somehow?
                pass

        if (len(encoder['right_trigger']) > 1):
            from pynput import keyboard
            try:
                keys = keyboard.HotKey.parse(encoder['right_trigger'])
                for i in range(len(keys)):
                    keys[i] = TerminalKeyInput._listener.canonical(keys[i])
                TerminalKeyInput._hotkeys.append(keyboard.HotKey(keys, TerminalKeyInput.createPressFun(encoder['right_trigger'])))
            except Exception as e:
                # TODO: Do we want to handle this somehow?
                pass
        return True

    @staticmethod
    def initEncoder(encoder):
        """ Initializes an encoder

        Args:
            encoder (Dictionary): Info about the encoder
        """
        if (encoder['left_trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % encoder['left_trigger'])
            return False
        if (encoder['right_trigger'] in TerminalKeyInput._keys):
            Printer.print("Duplicate trigger '%s', ignoring" % encoder['right_trigger'])
            return False
        TerminalKeyInput._keys[encoder['left_trigger']] = "_left_{}".format(encoder['name'])
        TerminalKeyInput._keys[encoder['right_trigger']] = "_right_{}".format(encoder['name'])
        return True

    @staticmethod
    def takeInput(str):
        """ Manually input a key for all 'key_input' type inputs

        Args:
            str (string): Anything, will be ignored if not registered
        """
        TerminalKeyInput.handleInput(str)

    @staticmethod
    def getNameString(key):
        if ("_button_" in key):
            return key.replace("_button_", "")
        elif("_left_" in key):
            return key.replace("_left_", "")
        elif("_right_" in key):
            return key.replace("_right_", "")
        return key

    @staticmethod
    def removeKey(key):
        """ Remove a key from the system

        Args:
            key (dict): The key input unit
        """
        if (key['trigger'] in TerminalKeyInput._keys):
            del TerminalKeyInput._keys[key['trigger']]

        if key['trigger'] in TerminalKeyInput._keyInterrupts:
            del TerminalKeyInput._keyInterrupts[key['trigger']]

        for item in TerminalKeyInput._keys.keys():
            name = TerminalKeyInput.getNameString(TerminalKeyInput._keys[item])
            if (name == key['name']):
                del TerminalKeyInput._keys[item]
                return

    @staticmethod
    def handleInput(str):
        """ Handles any input, and sends out a router message

        Args:
            str (string): Anything
        """
        map = TerminalKeyInput._keys
        if (str in map):
            # We send both down and up, since there is only ever one event for non interrupts
            val = map[str]
            if ("_button_" in val):
                val = map[str].replace("_button_", "")
                router.sendMessage(InputCommand(val, TerminalKeyInput.highValue))
                router.sendMessage(InputCommand(val, TerminalKeyInput.lowValue))
            elif("_left_" in val):
                val = val.replace("_left_", "")
                router.sendMessage(InputCommand(val, constants.ENCODER_LEFT))
            elif("_right_" in val):
                val = val.replace("_right_", "")
                router.sendMessage(InputCommand(val, constants.ENCODER_RIGHT))

class InputInitializer():
    """ Handles initializing all input
    """

    # Lets us know if we have already imported the pi modules.
    # We import only when needed so that this does not crash on a normal computer
    _importedPI = False

    @staticmethod
    def initInput(inputUnit):
        """ Inits some inputUnit. Will print an error if invalid

        Args:
            inputUnit (Dictionary): information about the inputUnit
        """
        if (type(inputUnit) != InputUnit):
            inputUnit = InputUnit(inputUnit)
        if (inputUnit['type'] == 'button'):
            return InputInitializer.initButton(inputUnit)
        elif (inputUnit['type'] == 'encoder'):
            return InputInitializer.initEncoder(inputUnit)
        else:
            Printer.print("'%s' is not a supported type" % inputUnit['type'])
        return False

    @staticmethod
    def removeInput(inputUnit):
        """ Removes a 'button'

        Args:
            button (Dictionary): Info about the button
        """
        if (inputUnit['mechanism'] in ['key_input', 'key_interrupt']):
            TerminalKeyInput.removeKey(inputUnit)
            return True
        elif (inputUnit['mechanism'] == 'rpi_gpio'):
            if (not InputInitializer._importedPI):
                return False
            # TODO: Do we need to support this?
        return False

    @staticmethod
    def initButton(button):
        """ Inits a 'button'

        Args:
            button (Dictionary): Info about the button
        """
        # Default to key_interrupt
        if (button['mechanism'] == 'key_input'):
            return TerminalKeyInput.initKey(button)
        elif (button['mechanism'] == 'key_interrupt'):
            return TerminalKeyInput.registerKeyInterrupt(button)
        elif (button['mechanism'] == 'rpi_gpio'):
            if (not InputInitializer._importedPI):
                from .pi_input_initializer import PiButton
                from .pi_input_initializer import PiEncoder
            PiButton(button)
        else:
            Printer.print("'%s' is not a supported button mechanism" % button['mechanism'])
            return False
        return True

    @staticmethod
    def initEncoder(encoder):
        """ Init a new encoder

        Args:
            encoder (Dictionary): Info about the encoder
        """
        # Default to key_interrupt
        if (encoder['mechanism'] == 'key_input'):
            return TerminalKeyInput.initEncoder(encoder)
        elif (encoder['mechanism'] == 'key_interrupt'):
            return TerminalKeyInput.registerEncoderInterrupt(encoder)
        elif (encoder['mechanism'] == 'rpi_gpio'):
            if (not InputInitializer._importedPI):
                from .pi_input_initializer import PiEncoder
                from .pi_input_initializer import PiButton
            PiEncoder(encoder)
        else:
            Printer.print("'%s' is not a supported encoder mechanism" % encoder['mechanism'])
            return False
        return True
