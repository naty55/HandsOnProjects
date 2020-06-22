from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from os import urandom
from client import Client
from time import sleep


NAME_KEY = 'name'
client = None

app = Flask(__name__)
app.secret_key = urandom(16)
clients = {}


def create_client(name, email, password):
    """
    handle client to prevent redundant connections
    and check if there is change in the name if so close previous client
    and start new one, return the status of client just created
    :param name: str
    :param email: str
    :param password: str
    :return: int
    """
    global clients
    exists = clients.get(name, False)

    if not exists:
        new_client = Client(name, email, password)
        sleep(0.1)
        print("STATUS WE GOT FOR", new_client.name,  "IS", new_client.status)

        if new_client.status == 0:
            clients[name] = new_client

        return new_client.status


@app.route("/")
def home():
    """
    Display home page and if there is active session handle it
    :return: Html rendered Home page with client name if exists
    """
    name = session.get(NAME_KEY, None)

    return render_template("index.html", user=name)


@app.route("/about")
def about():
    """
    Display about page
    :return: HTML rendered page
    """
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    method = request.method
    name = session.get(NAME_KEY, None)

    if name:  # if there is an active session
        return redirect(url_for('chatroom', usr=name))

    if method == "POST":  # if form is sent handle it

        try:  # try to get name from the form
            name = request.form["inputName"]
            email = request.form["inputEmail"]
            password = request.form['inputPass']

            if not all((name, email, password)):
                raise Exception("one or more params are missing")

        except Exception as e:
            print("[EXCEPTION]", e)
            return redirect(url_for('register'))

        else:  # if successfully open session with the name
            status = create_client(name, email, password)

            if status == 0:  # if successfully recorded redirect to chatroom
                print(f"[OK] {name} just registered in ")
                session[NAME_KEY] = name
                return redirect(url_for("chatroom", usr=name))
            else:  # else send error code
                return jsonify(status=status)

    return render_template("register.html")  # if exception occurred return login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        name = session.get(NAME_KEY, None)
        if name:  # if there is an active session
            return redirect(url_for('chatroom', usr=name))

        name = request.form['Name']
        password = request.form['Password']
        print(name, "is trying to log in with this password", password)
        status = create_client(name, email='', password=password)
        print("and its status is", status)
        if status == 0:
            print(name, "just logged in with password", password)
            session[NAME_KEY] = name
            return redirect(url_for("chatroom", usr=name))
        else:
            return jsonify(status=status)


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
        return redirect(url_for("register"))


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
    info = 'none'

    client = clients.get(name, None)
    if client:
        new_messages = client.get_messages()
        info = client.get_info()

    return jsonify(messages=new_messages, info=info)


if __name__ == '__main__':
    app.run(host='192.168.43.188', debug=True)
