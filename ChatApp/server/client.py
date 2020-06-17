from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from time import sleep
from ChatApp.protocol_requests import MPFCSResponse
from traceback import format_exc
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

        self.record()
        sleep(0.1)
        self.info()

    def receive(self):
        """
        receive messages from server
        :return: None
        """
        while self.is_alive():
            try:
                msg = MPFCSResponse(self.client_socket.recv(self.BUFSIZ))
                _type = msg.type

                if _type == "{quit}":
                    self.client_socket.close()

                elif _type == "{message}":
                    self._lock.acquire()
                    self.messages.append(msg.text)
                    self._lock.release()

                elif _type == '{record}':
                    print("There was a problem", msg.get_params())
                    self.client_socket.close()

            except Exception as e:
                print("Exception:", e)
                print(format_exc())
                break

    def record(self):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        record = "{record}"

        msg = f"{record} {self.name} {self.email} {self.password}\n\r"
        self.send(msg)

    def info(self):
        self.send("{info}\n\r")

    def talk(self, msg):
        msg = "{talk}\n\r" + msg
        self.send(msg)

    def send(self, msg):
        if not self.is_closed():
            msg = bytes(msg, CODEC)
            self.client_socket.send(msg)
        else:
            print(self.name, "Connection closed")

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
        msg = "{quit}\n\r"
        self.send(msg)

    def is_closed(self):
        return self.client_socket._closed

    def is_alive(self):
        return not self.client_socket._closed
