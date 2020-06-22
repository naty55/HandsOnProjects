from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from time import sleep
import json
from ChatApp.protocol_requests import MPFCSResponse
from traceback import format_exc
from ChatApp.settings import CODEC, BUFSIZ, ADDR


class Client:
    """
    class object for communication
    """

    def __init__(self, name, email, password):
        """
        Init object and send name to server
        :param name: str
        """
        self.name = name
        self.email = email
        self.password = password

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(ADDR)

        self.messages = []
        self._info = {}

        self._lock = Lock()

        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

        # indicate if there were issues with recording
        self.status = 0

        if self.email:  # try to record user
            self.record()
        else:  # else try to log him in
            self.check()

    def receive(self):
        """
        receive messages from server
        :return: None
        """
        while self.is_alive():
            try:
                msg = MPFCSResponse(self.client_socket.recv(BUFSIZ))
                _type = msg.type

                if _type == "{quit}":
                    self.client_socket.close()

                elif _type == "{message}":
                    self._lock.acquire()
                    self.messages.append(msg.text)
                    self._lock.release()

                elif _type == '{record}':
                    print("There was a problem", msg.get_params())
                    self.status = msg.get_params()[0]
                    self.client_socket.close()

                elif _type == "{info}":
                    # convert to json and store it
                    to_json = msg.text.replace("'", "\"")
                    self._info = json.loads(to_json)

                elif _type == '{check}':
                    print("Status of this client is")
                    print(msg.get_params()[0])
                    self.status = msg.get_params()[0]

            except Exception as e:
                print("Exception:", e)
                print(format_exc())
                break

    def record(self):
        """
        send messages to server
        :return: None
        """
        record = "{record}"
        msg = f"{record} {self.name} {self.email} {self.password}\n\r"

        self.send(msg)

    def talk(self, msg):
        msg = "{talk}\n\r" + msg
        self.send(msg)

    def check(self):
        check = '{check}'
        self.send(f"{check} {self.name} {self.password}\n\r")

    def send(self, msg):
        if self.is_alive():
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

    def get_info(self):
        return self._info

    def is_closed(self):
        return self.client_socket._closed

    def is_alive(self):
        return not self.client_socket._closed
