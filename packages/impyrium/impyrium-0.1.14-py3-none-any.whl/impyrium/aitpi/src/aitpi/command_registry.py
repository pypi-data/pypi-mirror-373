from genericpath import isdir
from .message import *
from .mirrored_json import MirroredJson
from . import router
from .folder_watch import FolderWatch
import os
import time

from .printer import Printer

class CommandRegistry():
    """ Represents a 'registry' of all commands that the user can execute
    """

    _registries = []

    @staticmethod
    def findByProperty(array, propertyName, propertyVal):
        """ Find an item in an array by a property of that item

            Returns:
                bool: if contains
        """
        index = 0
        for item in array:
            if (item[propertyName] == propertyVal):
                return index, item
            index += 1
        return -1, None

    def __init__(self, commandRegJson=None, foldersJson=None):
        """ Setup data structures
        """
        self.regFile = commandRegJson
        self.foldersFile = foldersJson
        self._commands = None
        self._foldersForCommands = None
        self._commands = MirroredJson(commandRegJson, default=[])
        self._foldersForCommands = MirroredJson(foldersJson) if foldersJson != None else None
        router.addConsumer(
            [CommandRegistryCommand.msgId],
            self
        )
        if (self._foldersForCommands != None):

            # Watch all the folders
            self.initFoldersForCommands()

            # Remove all old foldered commands
            self.cleanAllFolderCommands()

            # Reload all commands from the folders
            for folder in range(0, len(self._foldersForCommands)):
                self.reloadFolder(self._foldersForCommands[folder]['path'])
        CommandRegistry._registries.append(self)

    def __str__(self):
        return str(self._commands.file)

    def __repr__(self):
        return str(self)

    def cleanAllFolderCommands(self):
        """ Removes all folderd commands from the json file
        """
        for item in self._foldersForCommands._settings:
            if (item == None):
                return
            # Clear out all old commands
            # We assume the folder has changed entirely
            commands = self.getCommandsById(item['id'])
            index = 0
            for command in commands:
                if 'path' in command:
                    self._commands.remove(command)
                index += 1
        self.save()

    def initFoldersForCommands(self):
        """ Takes care of initalizing the foldersForCommands setup
        """

        # Now we need to subscribe to the folder messages
        router.addConsumer(
            [FolderMessage.msgId],
            self
        )
        for folder in self._foldersForCommands._settings:
            if (not isdir(folder['path'])):
                Printer.print("Did not find dir '{}' creating...".format(folder['path']))
                os.system("mkdir {}".format(folder['path']))
                time.sleep(0.1)
            try:
                isint = False
                try:
                    int(folder['id'])
                    isint = True
                except:
                    pass
                if (isint and int(folder['id']) < 0):
                    Printer.print("Message ID below zero for '%s'" % folder['path'], Printer.WARNING)
                    Printer.print("- Unsupported behavior, negative numbers reserved for AITPI.", Printer.WARNING)
                else:
                    FolderWatch.watchFolder(folder['path'], FolderMessage.msgId)
            # TODO: Check exception type so we don't say this is an invalid ID when another error occured
            except:
                Printer.print("Invalid folder message id '%s'" % folder['id'], Printer.ERROR)
            # Add watch to every folder

    @staticmethod
    def contains(id, command):
        """ Returns whether the command exists in this registry
        """
        if (CommandRegistry.getCommand(id, command) == None):
            return False
        return True

    @staticmethod
    def getCommand(id, command):
        for registry in CommandRegistry._registries:
            index, c = registry._commands.findByMultiProperties([('id', id), ('name', command)])
            if c is not None:
                return c
        return None

    @staticmethod
    def getAllCommandsGlobal():
        ret = []
        for registry in CommandRegistry._registries:
            ret.extend(registry._commands._settings)
        return ret

    @staticmethod
    def getFolder(foldersFile, name):
        for registry in CommandRegistry._registries:
            if (registry.foldersFile != foldersFile):
                continue
            for index in range(0, len(registry._foldersForCommands)):
                folder = registry._foldersForCommands[index]
                if (folder['name'] == name):
                    return folder
        return None

    def reloadFolder(self, folder):
        """ Reloads all the command folders
        """
        index, item = self._foldersForCommands.findByProperty(folder, 'path')
        if (item == None):
            return
        commandsToClean = []
        index = 0
        for command in self._commands:
            if command['id'] == item['id']:
                self._commands.remove(command)

        # Add all the files to the registry
        for root, dirs, files in os.walk(
            folder,
            topdown=False
            ):
            for name in files:
                msgId = item['id']
                val = {}
                val['id'] = msgId
                val['input_type'] = item['input_type']
                val['path'] = folder
                val['name'] = name
                self._commands.append(val)
        # Update the mirrored json
        self.save()

    def getAllCommands(self):
        """ Gets the list of commands

        Returns:
            list: commands
        """
        return self._commands

    def getCommandsById(self, id):
        """ Gets a list of commands by type

        Returns:
            list: commands
        """
        ret = []
        for command in self._commands:
            if command['id'] == id:
                ret.append(command)
        return ret

    def getIds(self):
        """ Returns all types in the registry

        Returns:
            list: list of all types
        """
        ret = []
        for command in self._commands:
            if command['id'] not in ret:
                ret.append(command['type'])
        return ret

    def addCommand(self, name, messageID, inputType):
        """ Adds a command to the library

        Args:
            name (str): The name of the command
            messageID (int): The message id the command is sent to

        Returns:
            [type]: True if added. False if duplicate (not added)
        """
        if (self.contains(messageID, name)):
            Printer.print("Cannot add '{}', duplicate name".format(name))
            return False
        else:
            self._commands.append({ "id": messageID, "input_type": inputType, 'name': name})
        self.save()
        return True

    def removeCommand(self, name):
        """ Removes a command

        Args:
            name (str): The name to remove
        """
        index, item = self._commands.findByProperty(name)
        if item:
            self._commands.pop(index)
            self.save()

    def clearType(self, T):
        """ Removes all the commands of a type

        Args:
            T (string): the type
        """
        purgeList = []
        index = 0
        for command in self._commands:
            if command['type'] == T:
                purgeList.append(index)
            index += 1
        for purge in purgeList:
            self._commands.pop(purge)

    def save(self):
        """ Saves all the commands to the mirrored json
        """
        self._commands.save()

    def consume(self, msg):
        """ Handles sending actuall commands,
            and watches folder commands for changes.

        Args:
            msg (Message): Either a command, or a folder update
        """
        if (msg.msgId == CommandRegistryCommand.msgId):
            self.send(msg)
        elif (msg.msgId == FolderMessage.msgId):
            self.reloadFolder(msg.data)

    def send(self, msg):
        """ Handles sending a command to where the library says

        Args:
            command (unknown): Some data that will be sent
        """
        action = msg.event
        type = msg.type
        idx, command = self._commands.findByMultiProperties([('id', msg.id), ('name', msg.name)])
        if (command is not None):
            if (command['input_type'] != type):
                Printer.print("Mismatched input_type for command '%s'" % command['name'], Printer.WARNING)
            msg = InputMessage(command['name'], action, command)
            msg.msgId = command['id']
            router.sendMessage(msg)
            return

    def updateFromFile(self):
        self._commands.load()