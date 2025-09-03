from .message import CleanUp
from .printer import Printer
from . import router
from .command_registry import CommandRegistry
from .input_converter import InputConverter
from .message import *
from .printer import Printer
from .input_initializer import TerminalKeyInput
from .input_initializer import *
from .constants import *
from .input_unit import InputUnit
from . import pyqt6_key_map

_initRegistry = False

def addRegistry(registryJson, folderedCommandsJson=None):
    """ Adds a new command registry to Aitpi

    Args:
        registryJson (string): path to a json file
        folderedCommandsJson (string, optional): path to a json file, defaults to None
    """
    CommandRegistry(registryJson, folderedCommandsJson)
    global _initRegistry
    _initRegistry = True

def initInput(inputJson):
    """ Initializes the input json

    Args:
        inputJson (string): path to a json file
    """
    global _initRegistry
    if (_initRegistry == False):
        Printer.print("Command registry must be added first", Printer.ERROR)
    else:
        InputConverter.init(inputJson)

def shutdown():
    """ Disables the Aitpi TODO: Does nothing
    """
    router.sendMessage(CleanUp())

def takeInput(input):
    """ Takes arbitrary string input to pass into the command system

    Args:
        input (string): Anything
    """
    TerminalKeyInput.takeInput(input)

def addCommandToRegistry(registryFile, command, id, inputType):
    """ Adds a command to the registry

    Args:
        registryFile (string): The path to the json file the registry mirrors
        command (string): string denoting the name of the command
        id (int): The id the command will be sent over
        type (string): The type of the new command
        inputType (string): the type of input 'button', 'encoder'
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.addCommand(command, id, inputType)

def clearCommandTypeInRegistry(registryFile, type):
    """ Clears all commands from a 'type' in a registry

    Args:
        registryFile (string): The path to the json file the registry mirrors
        type (string): The type to clear
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.clearType(type)
            break

def updateRegistryFromFile(registryFile):
    """ Updates registry from file

    Args:
        registryFile (string): The path to the json file the registry mirrors
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.updateFromFile()
            break

def removeCommandFromRegistry(registryFile, command):
    """ Removes a command from the registry

    Args:
        registryFile (string): The path to the json file the registry mirrors
        command (string): The name of the command
        type (string): The type of the command
    """
    for registry in CommandRegistry._registries:
        if (registry.regFile == registryFile):
            registry.removeCommand(command)

def changeInputRegLink(nameOrTrigger, commandId, commandName):
    """ Changes the reg link of an input unit

    Args:
        nameOrTrigger (string): The input unit name, or trigger string
        regLink (string): The new link to a command registry
    """
    InputConverter.change(nameOrTrigger, commandId, commandName)

def getFolderedCommands(foldersFile, folderedName):
    """[summary]

    Args:
        foldersFile (string): The path to the json file the registry mirrors
        folderedName (string): The name of the foldered comands entry
    """
    return CommandRegistry.getFolder(foldersFile, folderedName)

def getCommandsByInputType(inputType):
    commands = CommandRegistry.getAllCommandsGlobal()
    ret = []
    for command in commands:
        if command['input_type'] == inputType:
            ret.append(command)
    return ret

def getCommandsById(T):
    ret = []
    for registry in CommandRegistry._registries:
        ret.extend(registry.getCommandsById(T))
    return ret

def getCommands():
    """ Gets all the commands from any command registry

    Returns:
        []: an array of all command names
    """
    return CommandRegistry.getAllCommandsGlobal()

def getCommandsByRegistry(registry):
    """ Gets all the commands from any command registry

    Returns:
        []: an array of all command names
    """
    for reg in CommandRegistry._registries:
        if reg.regFile == registry:
            return reg._commands._settings
    return []

def getInputs():
    """ Get all of the inputs from json
    """
    return InputConverter._inputUnits._settings

def getInputsByType(T):
    """ Get inputs by their type
    """
    ret = []
    for input in InputConverter._inputUnits:
        if input['type'] == T:
            ret.append(input)
    return ret

def addInput(inputUnit):
    """ Adds an input to the list of possible inputs

    Args:
        trigger (string): The input trigger
        name (string): The name of the input (optional)
        inputType (string): The type of the input
        mechanism (string): The mechanism of the input
    """
    if type(inputUnit) != InputUnit:
        inputUnit = InputUnit(inputUnit)
    InputConverter.addInput(inputUnit)

def removeInput(inputUnit):
    """ Remove an input from the inputs list

    Args:
        inputUnit (string): The name, trigger, or input unit of the input
    """
    InputConverter.removeInput(inputUnit)

def recordKeyCombo():
    """ Records a new keyboard combonation for key_interrupt input

    Returns:
        string: A string signifying the key combo
    """
    pass

def pyqt6KeyPressEvent(event):
    """ Takes in key events from pyqt6 for seemless integration
    """
    input_initializer.TerminalKeyInput.onPress(pyqt6_key_map.pyqt6Map[event.key()])

def pyqt6KeyReleaseEvent(event):
    """ Takes in key events from pyqt6 for seemless integration
    """
    input_initializer.TerminalKeyInput.onRelease(pyqt6_key_map.pyqt6Map[event.key()])

def registerKeyHandler(fun):
    """ Takes a function that can handle key interrupts directly
        fun(char, aitpi.BUTTON_PRESS | aitpi.BUTTON_RELEASE)
    """
    input_initializer.TerminalKeyInput.registerKeyHandler(fun)

def removeKeyHandler(fun):
    """ Remove function from the key handler list
    """
    input_initializer.TerminalKeyInput.removeKeyHandler(fun)
