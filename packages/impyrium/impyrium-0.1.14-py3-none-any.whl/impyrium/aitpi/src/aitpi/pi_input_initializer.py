from os import stat
from .printer import Printer
from . import router
from .message import *
import RPi.GPIO as GPIO
import threading
from time import sleep
from . import constants

# lets us know if we already inited the pi system
__initedPi = False

def _piInit():
    """ Initializes the pi system
    """
    global __initedPi
    if (not __initedPi):
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
    __initedPi = True

class PiEncoder():
    """ Represents an encoder on a raspberry pi
    """

    # A static list of all encoders created
    _initedEncoders = []

    def __init__(self, encoder):
        """ Creates a new encoder, and registers to the static list

        Args:
            encoder (Dictionary): Info about the encoder
        """
        try:
            self.triggerL = int(encoder['left_trigger'])
        except:
            Printer.print("Invalid left_trigger '%s' under '%s'" % (encoder['left_trigger'], encoder['name']))
            return

        try:
            self.triggerR = int(encoder['right_trigger'])
        except:
            Printer.print("Invalid right_trigger '%s' under '%s'" % (encoder['right_trigger'], encoder['name']))
            return

        _piInit()
        self.encoder = encoder
        self.triggerLCounter = 1
        self.triggerRCounter = 1

        self.LockRotary = threading.Lock()
        try:
            GPIO.setup(self.triggerL, GPIO.IN)
            GPIO.setup(self.triggerR, GPIO.IN)
            GPIO.add_event_detect(self.triggerL, GPIO.RISING, callback=self.handleInterrupt)
            GPIO.add_event_detect(self.triggerR, GPIO.RISING, callback=self.handleInterrupt)
        except Exception:
            Printer.print("Failed to init encoder '%s'" % encoder['name'])
            return
        PiEncoder._initedEncoders.append(self)
        return

    def handleInterrupt(self, leftOrRight):
        """ Hanles interrupts from the GPIO system

        Args:
            leftOrRight (int): Could be the left or right gpio
        """
        triggerL = GPIO.input(self.triggerL)
        triggerR = GPIO.input(self.triggerR)

        if self.triggerLCounter == triggerL and self.triggerRCounter == triggerR:
            return

        self.triggerLCounter = triggerL
        self.triggerRCounter = triggerR

        if (triggerL and triggerR):
            self.LockRotary.acquire()
            if leftOrRight == self.triggerR:
                router.sendMessage(InputCommand(self.encoder['name'], "RIGHT"))
            else:
                router.sendMessage(InputCommand(self.encoder['name'], "LEFT"))
            self.LockRotary.release()
        return

class PiButton():
    """ Handles initalization and interrupt handling of pi buttons
    """

    BUTTON_BOUNCE = 25 # ms

    # Change these to UP DOWN or whatever you want
    highValue = constants.BUTTON_PRESS
    lowValue = constants.BUTTON_RELEASE

    # A static list of all pi buttons inited
    _buttons = []

    def __init__(self, button):
        """ Creates and adds a button to the static list

        Args:
            button (Dictionary): Info about the button
        """

        _piInit()
        try:
            GPIO.setup(int(button['trigger']), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except:
            Printer.print("Failed to setup button '%s'" % button['name'])
        try:
            GPIO.add_event_detect(int(button['trigger']), GPIO.BOTH, callback=self.press, bouncetime=PiButton.BUTTON_BOUNCE)
        except:
            Printer.print("Failed to add event interrupt to button '%s'" % button['name'])
        self.button = button

    def press(self, gpio):
        """ Event handler when gpio changes

        Args:
            gpio (int): GPIO pin number
        """

        if (GPIO.input(int(self.button['trigger'])) != 1):
            router.sendMessage(InputCommand(self.button['name'], PiButton.lowValue))
        else:
            router.sendMessage(InputCommand(self.button['name'], PiButton.highValue))

class PiCleanup():
    """ Cleans up the gpio upon shutdown
    """
    @staticmethod
    def consume(msg):
        GPIO.cleanup()

# We will listen for any cleanup messages
router.addConsumer([CleanUp.msgId], PiCleanup)
