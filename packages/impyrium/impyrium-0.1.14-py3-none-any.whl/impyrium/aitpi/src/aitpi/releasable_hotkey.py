from pynput import keyboard

class ReleaseableHotkey(keyboard.HotKey):
    """ Copied from pynput
    """
    def __init__(self, keys, on_activate, on_release):
        self._state = set()
        self._keys = set(keys)
        self._on_activate = on_activate
        self._on_release = on_release

    def clear(self):
        self._state.clear()

    def press(self, key):
        if key in self._keys and key not in self._state:
            self._state.add(key)
            if self._state == self._keys:
                self._on_activate()

    def release(self, key):
        """Updates the hotkey state for a released key.

        :param key: The key being released.
        :type key: Key or KeyCode
        """
        if key in self._state:
            if self._state == self._keys:
                self._on_release()
            self._state.remove(key)
