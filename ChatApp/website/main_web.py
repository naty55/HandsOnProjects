from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from os import urandom
from client import Client


NAME_KEY = 'name'
client = None

app = Flask(__name__)
app.secret_key = urandom(16)
clients = {}


def handle_clients(name, email, password):
    """
    handle client to prevent redundant connections
    and check if there is change in the name if so close previous client
    and start new one
    :param name: str
    :return: None
    """
    global clients
    exists = clients.get(name, False)

    if not exists:
        new_client = Client(name, email, password)
        clients[name] = new_client


@app.route("/<name>")
@app.route("/")
def home(name=None):
    """
    Display home page and if there is active session handle it
    :param name: optional str[name]
    :return: Html rendered Home page with client name if exists
    """
    name = session.get(NAME_KEY, None)
    print(name)
    if name:  # There is active session
        handle_clients(name)   # check for its client or create new one

    return render_template("index.html", user=name)


@app.route("/about")
def about():
    """
    Display about page
    :return: HTML rendered page
    """
    print(session.get(NAME_KEY, None))
    return render_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    method = request.method
    name = session.get(NAME_KEY, None)

    if name:  # if there is an active session
        return redirect(url_for('chatroom', usr=name))

    if method == "POST":  # if form is sent handle it
        try:  # try to get name from the form
            name = request.form["inputName"]

            email = request.form["inputEmail"]
            password = request.form['inputPass']

        except Exception as e:
            print("[EXCEPTION]", e)
            return redirect(url_for('login'))

        else:  # if successfully open session with the name
            session[NAME_KEY] = name
            handle_clients(name, email, password)
            return redirect(url_for("chatroom", usr=name))  # and redirect to chatroom

    return render_template("login.html")  # if exception occurred return login page


@app.route("/logout", methods=["GET"])
def logout():
    """
    handling logging out by removing session, closing connection from chat sever,
    and removing from clients dict
    :return: redirect response to home page
    """

    name = session.get(NAME_KEY, None)
    client = clients.get(name, None)
    if client:  # check if there is client with that name
        client.disconnect()  # if so disconnect
        del clients[name]    # and remove from clients dict
    session.pop(NAME_KEY, None)

    return redirect(url_for("home"))  # and finally redirect back to home page


@app.route("/<usr>/chatroom")
def chatroom(usr):
    """
    display chatroom to client
    :param usr: str
    :return: if usr has session open to chatroom else to redirect login page
    """
    name = session.get(NAME_KEY, None)
    print(name)
    if usr == name:
        return render_template("chatroom.html", user=usr)
    else:
        return redirect(url_for("login"))


@app.route('/send', methods=["POST"])
def send():
    name = session.get(NAME_KEY, None)
    try:
        message = request.get_json().get("message", None)
    except Exception as e:
        print("[EXCEPTION]", e)
        return 'none'

    print(name, " is sending ", message)

    client = clients.get(name, None)
    if client:
        client.talk(message)
    return "none"


@app.route('/update', methods=["GET"])
def update():

    name = session.get(NAME_KEY, None)
    new_messages = "Not connected"

    client = clients.get(name, None)
    if client:
        new_messages = client.get_messages()
    print(name, new_messages)
    return jsonify(list=new_messages)


if __name__ == '__main__':
    app.run(host='192.168.43.188')
