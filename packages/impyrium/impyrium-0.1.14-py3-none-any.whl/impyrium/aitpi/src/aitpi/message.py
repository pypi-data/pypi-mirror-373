class Message():
    """Simplist message class
    """
    msgId = None
    def __init__(self, data):
        """ Inits data

        Args:
            data (unknown): Just some data to send
        """
        self.data = data

class CommandRegistryCommand(Message):
    """ Sent to command library
    """
    msgId = -1002
    def __init__(self, id, name, action, type):
        self.name = name
        self.id = id
        self.event = action
        self.type = type

class InputCommand(Message):
    """ When a button is pressed
    """
    msgId = -1003

    def __init__(self, data, action):
        super().__init__(data)
        self.event = action

class FolderMessage(Message):
    """ When a folder changes
    """
    msgId = -1004

class InputMessage(Message):
    """ Class for sending messages to the user's space. 'msgId' will change based on json
    """
    msgId = -1005

    def __init__(self, name, action, attributes):
        self.name = name
        self.event = action
        self.attributes = attributes

    def __str__(self) -> str:
        return f"{{ 'name': {self.name}, 'event': {self.event}, 'attributes': {self.attributes} }}"

class CleanUp(Message):
    """ A cleanup message sent out to Aitpi signaling shutdown
    """
    msgId = -1006

    def __init__(self):
        pass
