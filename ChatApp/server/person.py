class Person:
    """
    represents a person, holds name, client socket and its IP address
    """
    def __init__(self, addr, client):
        self.addr = addr
        self.client = client

        self.name = None

    def set_name(self, name):
        """
        Sets the person name
        :param name: str
        :return: None
        """
        self.name = name

    def __repr__(self):
        return f"Person{self.addr}, {self.name}"

    def is_alive(self):
        return not self.client._closed

