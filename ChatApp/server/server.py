from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time

from person import Person
from DataBase import DataBase

# Global Constants
HOST = 'localhost'
PORT = 5500
BUFSIZ = 1024
MAX_CONNECTIONS = 10
ADDR = (HOST, PORT)
CODEC = 'utf8'
DB = DataBase('test.db')

# Global Variables
persons = []
Names = []
number_of_conn = 0
my_name = "Natty"


SERVER = socket(AF_INET, SOCK_STREAM)  # start server
SERVER.bind(ADDR)


def broadcast(msg, name=""):
    """
    Neat the name and then
    Send the new message to all clients
    :param msg: bytes["utf8"]
    :param name: str
    :return: None
    """
    if name:
        name += " : "
    for person in persons:
        try:
            client = person.client
            client.send(bytes(name, CODEC) + msg)

        except Exception as e:
            print(f"[EXCEPTION] could'nt send to {person.addr} at {time.time()}", e)


def wait_for_connections():
    """
    wait for connection from new clients once connected start new thread
    :return: None
    """
    global number_of_conn
    while True:
        try:
            client, addr = SERVER.accept()
            number_of_conn += 1
            person = Person(addr, client)
            persons.append(person)
            print(f"[CONNECTED] {addr} connected to the server at {time.time()}")
            print(number_of_conn, "people are connected now")
            client.send(bytes("Greeting from cave! ", CODEC))
            Thread(target=handle_client, args=(person,)).start()
        except Exception as e:
            print("[Failure]", e)
            break

    print("SERVER CRASHED...")


def handle_client(person):
    """
    Thread to handle all messages from client
    :param person: Person
    :return: None
    """
    client = person.client

    # First message received is always the person's name
    try:
        name = client.recv(BUFSIZ).decode(CODEC)
        Names.append(name)
        print(Names)
    except Exception as e:
        print("[EXCEPTION]", e)
        persons.remove(person)
        client.close()
        print(f"[DISCONNECTED] {person.addr} disconnected to the sever at {time.time()}")
        return
    else:
        person.set_name(name)

    time.sleep(0.1)
    welcome_msg = bytes(name + " welcome to our chat send {quit} any time to leave", CODEC)
    client.send(welcome_msg)  # Greet person that he is in the chat and inform him how he can leave

    msg = bytes(f"{name} has joined the chat!", CODEC)
    broadcast(msg)  # Inform all clients about the new member

    while True:  # wait for any message from person
        try:
            msg = client.recv(BUFSIZ)
            print(f"{name}: {msg.decode(CODEC)}")
            if msg == bytes("{quit}", CODEC):  # if message is {quit} disconnect person
                handle_socket_closing(person)
                break

            else:  # otherwise send to all other clients
                broadcast(msg, name)

        except Exception as e:
            handle_socket_closing(person, e)
            break


def handle_socket_closing(person, e=None):
    """
    handles expected and unexpected happened by error client socket closing
    removes persons from list and print logs to the screen
    :param person: person
    :param e: error message
    :return: None
    """
    global number_of_conn
    number_of_conn -= 1
    Names.remove(person.name)
    print(number_of_conn, "people are connected")
    client = person.client
    if e:  # Check if error message exists
        # error occurred log error message
        print("[Exception]", e)
    else:
        client.send(bytes("{quit}", CODEC))

    client.close()
    persons.remove(person)
    if not e:
        # Inform everybody that that person has left
        broadcast(bytes(f"{person.name} has left the chat...", CODEC))

    print(f"[DISCONNECTED] {person.addr} disconnected to the server at {time.time()}")


def get_info():
    """
    get information about the status of people on the chat
    :return: info type:dict
    """
    info = {'count': number_of_conn,
            'names': Names,
            }
    return info


if __name__ == '__main__':
    SERVER.listen(MAX_CONNECTIONS)  # Listen for connections
    print("[STARTED] Waiting for connection....")
    ACCEPT_THREAD = Thread(target=wait_for_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    print("Closing server")
    SERVER.close()
