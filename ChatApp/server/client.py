from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from time import sleep


class Client:
    """
    class object for communication
    """
    # Global Constants
    HOST = "localhost"
    PORT = 5500
    BUFSIZ = 1024
    MAX_CONNECTIONS = 10
    ADDR = (HOST, PORT)
    CODEC = 'utf8'

    def __init__(self, name):
        """
        Init object and send name to server
        :param name: str
        """
        self.name = name

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)

        self.messages = []

        self._lock = Lock()

        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()
        self.send(self.name)

    def receive(self):
        """
        receive messages from server
        :return: None
        """
        while True:
            try:
                msg = self.client_socket.recv(self.BUFSIZ).decode(self.CODEC)

                # Make sure memory safe to access
                self._lock.acquire()
                self.messages.append(msg)
                self._lock.release()
                # print(msg)
                if msg == "{quit}":
                    self.client_socket.close()
                    break

            except Exception as e:
                print("Exception:", e)
                break

    def send(self, msg):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        if self.receive_thread.is_alive():
            self.client_socket.send(bytes(msg, "utf8"))
            return

        print("The connection is closed")

    def get_messages(self):
        """
        return list of messages
        :return: list[str]
        """
        msgs_copy = self.messages[:]
        print(self.name)

        # Make sure memory safe to access
        self._lock.acquire()
        self.messages = []
        self._lock.release()
        return msgs_copy

    def disconnect(self):
        """
        Disconnect server by sending {quit} message
        :return : None
        """
        if self.receive_thread.is_alive():
            self.send("{quit}")
        else:
            print("The connection already closed!")

    def is_closed(self):
        return self.client_socket._closed
