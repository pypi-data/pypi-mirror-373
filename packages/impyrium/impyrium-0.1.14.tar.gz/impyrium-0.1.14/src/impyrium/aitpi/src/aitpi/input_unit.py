
class InputUnit():
    def __init__(self, value={}):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def getValue(self):
        return self.value

    def __getitem__(self, item):
        if (item in self.value):
            return self.value[item]
        if (item == 'mechanism'):
            return "key_interrupt"
        if (item == 'type'):
            return "button"
        return ""

    def __setitem__(self, item, value):
        self.value[item] = value

    def __contains__(self, item):
        return item in self.value
