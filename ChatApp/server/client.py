from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from time import sleep
CODEC = 'utf8'

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

    def __init__(self, name, email, password):
        """
        Init object and send name to server
        :param name: str
        """
        self.name = name
        self.email = email
        self.password = password

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)

        self.messages = []

        self._lock = Lock()

        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

        self.send_record()

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
                if msg == "{quit}":
                    self.client_socket.close()
                    break
                # if msg

            except Exception as e:
                print("Exception:", e)
                break

    def send_record(self):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        record = "{record}"
        if self.receive_thread.is_alive():
            a = bytes(f"{record} {self.name} {self.email} {self.password}\n\r", "utf8")
            self.client_socket.send(a)
            return

        print("The connection is closed")

    def send(self, msg):
        if self.receive_thread.is_alive():
            a = bytes("{talk}\r\n" + msg, 'utf8')
            self.client_socket.send(a)

    def get_messages(self):
        """
        return list of messages
        :return: list[str]
        """
        msgs_copy = self.messages[:]

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
            self.client_socket.send(bytes("{quit}\n\r", CODEC))
        else:
            print("The connection already closed!")

    def is_closed(self):
        return self.client_socket._closed
