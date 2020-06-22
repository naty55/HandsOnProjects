from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime
import time
import traceback

from person import Person
from DataBase import DataBase

from ChatApp.protocol_requests import MPFCSRequest as req
from ChatApp.protocol_requests import response_message, response_record, response_info, response_check
from ChatApp.settings import CODEC, DATABASE_PATH, BUFSIZ, ADDR, MAX_CONNECTIONS


###################################################
#    This server works with a made up protocol only for
#    its own purpose, the protocol called "My Protocol For Chat Server Protocol" :P,
#    or in short "MPFCSP", (you can omit the last 'P' if you wish) ;).
#    and it goes like this:
#    the first line is the header line and it followed with '\n\r' to indicate the end of the header.
#    From there down is the body. the body supposed to contain
#    the message that is going to be displayed on the chat page.
#    The protocol takes place over Transmission protocol (like TCP, UDP)
#
#    #### Request ####
#
#    There are some keywords or methods for the header and every one of them
#    has to be wrapped in curly brackets:
#
#    --> {quit}:   tells the server to close the connection with client.
#
#    --> {record}: tells the server of user (either new or not)
#                  that wants to join th chat and it should be followed
#                  with 3 params right after it separated by space name, email, password.
#                  when user is recorded the server won't accept records messages anymore,
#                  and if the client wants to connect as another user he'll have to
#                  reconnect to server.
#
#    --> {talk}:   tells the server that the body contains message that
#                  should be broadcast to every client on the chat and of course
#                  to be recorded on the database.
#
#    --> {delete}: tells the server of message that should be deleted from the chat and
#                  the database. it should be followed with 1 param the id of this message.
#                  if the client has a permission for deleting that message, the message
#                  will be deleted and every client will get message telling him to delete
#                  that message.
#    --> {info}   :tells the server to send information about the chat e.g. how many are online etc..
#
#    --> {check}  :tells the server to check for specific user by name and password, must contain in
#                 the params name and password, the server returns check response with params
#                 0 or -1 for success and failure respectively
#
#    For example let's say there is new user wants to join the chat room here
#    is what he should do:
#    A) send first message '''{record} user_name user's_email, password\n\r'''
#    B) after he has got message inform him that his recording was success now he can talk
#       '''{talk}\n\r
#          message
#       '''
#    C) when he is done with his talking and wants to leave '''{quit}\n\r'''
#    and the connection will be closed.
#
#    #### Response ####
#
#    Until now we have talked about the request now let's talk about the response.
#    The response is just like the request the first line is the header and from
#    there down is the body.
#    Here are the methods for response:
#    --> {record}: tells the client that he should send record request in order to start
#                  chatting. it may happened if the client didn't send record request or sent it with name or email
#                  that is already in use for another client (even if that client is not connected at that time).
#                  The header may contain the problematic part of the request if exists, e.g. if email is already in
#                  use the param will be -3
#                  0 = ok, -1 = undetected, -2 = name is in use, -3 mail is in use
#
#    --> {message}: send the client new message that has arrived, the text message is in the body.
#
#    --> {update}:  tells the clients to update their messages entry. for example if user has deleted
#                   message then update message will be sent to all clients.
#
#    --> {info}  :  inform all clients how many people are on the chat and their names. the header is
#                   JSON object, info message can be sent from server even without client's request.
#
#    --> {check}  : after the server received a check request it sends check response with parameter 0
#                   or -1
#
#   That's it for now....


# Global Variables
persons = []
Names = []

SERVER = socket(AF_INET, SOCK_STREAM)  # start server
SERVER.bind(ADDR)
DB = DataBase(DATABASE_PATH)


def broadcast(msg='', method='{message}', name=""):
    """
    Neat the name and then
    Send the new message to all clients
    :param msg: str
    :param method: str
    :param name: str
    :return: None
    """
    message = bytes()
    if method == "{message}":
        if name:
            name += " : "
        message = response_message(name + msg)

    elif method == '{info}':
        message = response_info(get_info())

    for person in persons:
        try:
            person.client.send(message)

        except Exception as e:
            print(traceback.format_exc())
            print(f"[EXCEPTION] could'nt send to {person.addr} at {datetime.now()}", e)


def wait_for_connections():
    """
    wait for connection from new clients once connected start new thread
    :return: None
    """
    while True:
        try:
            client, addr = SERVER.accept()
            person = Person(addr, client)
            persons.append(person)

            print(f"[CONNECTED] {addr} connected to the server at {datetime.now()}")
            show_info()
            broadcast(method='{info}')

            client.send(response_message("Greeting from cave! "))
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

    # Before the user starts chatting he has to be recorded
    if get_user(person) == -1:  # There was problem with that person
        return

    name = person.name

    time.sleep(0.1)
    client.send(response_message(name + " welcome to our chat"))  # Greet person that he is in the chat
    broadcast(f"{name} has joined the chat!")  # Inform all clients about the new member

    while person.is_alive():  # wait for any message from person while connected
        time.sleep(0.1)

        try:
            request = req(client.recv(BUFSIZ))  # Get message from client
            _type = request.type

            if _type == "{quit}":  # if message is {quit} disconnect person
                handle_socket_closing(person)

            elif _type == '{talk}':  # if message is {talk} send message response to all other clients
                print(f"{name}: {request.text}")
                broadcast(request.text, name=name)
                DB.record_message(request.text, name)

            elif _type == '{delete}':  # if message is {delete} delete message from db
                pass  # delete from message db and broadcast to all users update message

            elif _type == '{info}':
                client.send(response_info(get_info()))

        except Exception as e:
            handle_socket_closing(person, e)


def handle_socket_closing(person, e=None):
    """
    handles expected and unexpected (usually happened by error) client socket closing
    removes persons from list and print logs to the screen
    :param person: person
    :param e: error message
    :return: None
    """

    if person.name:
        Names.remove(person.name)

    client = person.client
    if e:  # Check if error message exists
        # error occurred log error message
        print("[Exception]", e)
    else:
        client.send(bytes("{quit}", CODEC))

    client.close()
    print(f"[DISCONNECTED] {person.addr} disconnected from the server at {datetime.now()}")
    persons.remove(person)

    show_info()

    if not e:
        # Inform everybody that that person has left
        broadcast(f"{person.name} has left the chat...")


def get_info():
    """
    get information about the status of people on the chat
    :return: info type:dict
    """
    info = {"count": len(persons),
            "names": Names,
            }
    return info


def show_info():
    print("[INFO]", len(persons), "people are connected")


def get_user(person):
    """
    get from client his details like name, email and password
    using record response, and record them into database
    :param person: person that is not recorded
    :return: int if failed(-1)
    """

    while not person.name:  # run as long as the person didn't recorded
        status = -1
        try:
            request = req(person.client.recv(BUFSIZ))

            if request.type == '{record}':
                name, email, password = request.get_params()
                status = DB.record_user(name, email, password)

            elif request.type == '{check}':
                name, password = request.get_params()
                print(name, 'is trying to log in', password)
                status = DB.check_for(name, password)
                print("and it's status is", status)
                if status == 0:
                    Names.append(name)
                    person.set_name(name)
                else:
                    person.client.send(response_check(status))
                    handle_socket_closing(person)
                    return -1

        except Exception as e:
            # print(traceback.format_exc())
            handle_socket_closing(person, e)
            return -1

        else:
            print("status:", status)
            if status == 0:  # record succeeded
                Names.append(name)
                person.set_name(name)

            else:  # There was not record request or there was a problem with recording the user
                person.client.send(response_record(str(status)))


if __name__ == '__main__':
    SERVER.listen(MAX_CONNECTIONS)  # Listen for connections
    print("[STARTED] Waiting for connection....")
    ACCEPT_THREAD = Thread(target=wait_for_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    print("Closing server")
    SERVER.close()
