from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep

# Global Constants
HOST = "localhost"
PORT = 5500
BUFSIZ = 1024
MAX_CONNECTIONS = 10
ADDR = (HOST, PORT)
CODEC = 'utf8'

# Global Variables
messages = []

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)


def receive():
    """
    receive messages from server
    :return: None
    """
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode(CODEC)
            messages.append(msg)
            print('\r' + msg)
            if msg == "{quit}":
                client_socket.close()
                break

        except Exception as e:
            print("Exception:", e)
            break


def send(msg):
    """
    send messages to server
    :param msg: str
    :return: None
    """
    if client_thread.is_alive():
        client_socket.send(bytes(msg, "utf8"))
    else:
        print("\rThat's it you closed the connection!")


client_thread = Thread(target=receive)
client_thread.start()


# client_socket.close()
while client_thread.is_alive():
    sleep(0.5)
    send(input("-> "))
