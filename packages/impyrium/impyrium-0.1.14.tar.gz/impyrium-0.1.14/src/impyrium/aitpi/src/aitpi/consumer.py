from .printer import Printer
class Consumer():
    """The simplest consumer class
    """
    # isActive is static just to verify that it will always exist,
    # instances when edited will not change this value
    isActive = False
    def __init__(self):
        """inits the recieve buffer
        """
        self.mailBox = []

    def consume(self, mail):
        """called when you get mail

        Args:
            mail (Message): The mail recieved
        """
        Printer.print("Default comsumer recieved some message")
