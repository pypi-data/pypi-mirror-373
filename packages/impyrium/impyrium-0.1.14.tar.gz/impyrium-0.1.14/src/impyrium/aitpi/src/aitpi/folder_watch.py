import time
from .printer import Printer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from . import router
from .message import FolderMessage
from .message import Message

class FolderWatch():
    watchers = []
    def __init__(self):
        """ This is a fully static class
        """
        raise "Static class"

    # Will add a folder to be watched, and will send a message at any change with msgId
    @staticmethod
    def watchFolder(folder, msgId):
        """Watches a folder

        Args:
            folder (string): The folder you want to watch
            msgId ([type]): the message id that change notifications are sent with
        """
        Printer.print("Watching: '%s'" % folder)
        try:
            w = Watcher(folder, msgId)
            FolderWatch.watchers.append(w)
            w.run()
        except:
            Printer.print("Invalid folder '%s'" % folder, level=Printer.ERROR)

    @staticmethod
    def stop():
        """ Stops watching all folders
        """
        for w in FolderWatch.watchers:
            w.stop()

class Watcher(FileSystemEventHandler):
    def __init__(self, folder, msgId):
        """Inits

        Args:
            folder ([type]): [description]
            msgId ([type]): [description]
        """
        self.observer = Observer()
        self.folder = folder
        self.msgId = msgId

    def run(self):
        """ Runs the watching of a folder
        """
        self.observer.schedule(self, self.folder, recursive=True)
        self.observer.start()

    def stop(self):
        """ Stops watching a folder
        """
        self.observer.join()

    def on_any_event(self, event):
        """Handles events of folder changes

        Args:
            event (event): the event that has occured

        Returns:
            None: This will always return None
        """
        msg = Message(self.folder)
        msg.msgId = self.msgId
        if event.is_directory:
            return None
        elif (event.event_type == 'deleted' or event.event_type == 'created' or event.event_type == 'modified'):
            router.sendMessage(msg)