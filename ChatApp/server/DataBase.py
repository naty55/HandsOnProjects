import sqlite3
from sqlite3 import Error
import hashlib
from datetime import datetime
from threading import Lock


class Queue:
    def __init__(self):
        self.MESSAGES = []

    def append(self, action):
        self.locker.acquire()
        self.MESSAGES.append(action)
        self.locker.release()

    def get(self):
        messages = self.MESSAGES[:]
        self.locker.acquire()
        self.MESSAGES = []
        self.locker.release()
        return messages


q = Queue()


class DataBase:
    """ handle connection to database and manage it """
    def __init__(self, path):
        self.path = path
        self.rows = ['id', 'name', 'email', 'password', 'hash']
        self.locker = Lock()

        self.connection = self.connect()
        self.initialize()

    def connect(self):
        """
        Connect to SQLite database
        :return: sqlite3 connection
        """
        db = None
        try:
            db = sqlite3.connect(self.path, check_same_thread=False)
            print("[OK] connection to DB successful")
        except Error as e:
            print("[Exception]", e)

        return db

    def execute_query(self, query, success_msg='', params=None):
        """
        provide more convinient API for executing query on database
        :param query: str query you want to execute
        :param success_msg: str success message to be printed if execution went well
        :param params: tuple
        :return: 1 if success -1 otherwise
        """
        cursor = self.connection.cursor()
        try:
            self.locker.acquire()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            self.locker.release()

            if success_msg:
                print(success_msg)
            return 0  # return 0 if success

        except Error as e:
            print("[EXCEPTION]", e)
            # return -1 if failure
            return -1

    def initialize(self):
        """
        Initialize the database with messages table, and users table
        :return: None
        """
        query_create_messages = """
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT,
                time timestamp,
                FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """
        query_create_users = """
                    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    password TEXT,
                    hash TEXT
                    );
                    """
        self.execute_query(query_create_messages, "[OK] initialization of database successful")
        self.execute_query(query_create_users, "[OK] initialization of database successful")

    def read_query(self, query):

        cursor = self.connection.cursor()
        try:
            self.locker.acquire()
            cursor.execute(query)
            result = cursor.fetchall()
            # print("[OK] read query successful")
            self.locker.release()
            return result

        except Error as e:
            print("[EXCEPTION]", e)
            return -1

    def record_user(self, name, mail, password):
        query = f"""
        INSERT INTO  
         users (name, email, password, hash)
        VALUES
         (?, ?, ?, ?);
        """
        print("TRYING TO RECORD", name, mail, password)
        user_hash = hashlib.md5(bytes(name + mail + password, 'utf8')).hexdigest()
        if self.is_user(name):
            usr = self.get_user(name)
            if usr['hash'] == user_hash:  # this user had recorded already
                print(name, 'Just logged in')
                return 0
            return -2
        elif self.is_user(mail, key='email'):
            return -3  # This mail is in use already
        else:
            return self.execute_query(query, "[OK] user successfully recorded", (name, mail, password, user_hash))

    def record_message(self, message, name):
        """
        record message from user
        :param message: str
        :param name: str
        :return: 0 if success -1 otherwise
        """
        user_id = self.read_query(f"SELECT id from users WHERE name = '{name}'")
        if user_id:
            user_id = user_id[0][0]
        else:
            print("[EXCEPTION] No user with that name")
            return -1

        query = f"""
        INSERT INTO  
         messages (user_id, text, time)
        VALUES
         (?, ?, ?);
        """

        return self.execute_query(query, params=(user_id, message, datetime.now()))

    def get_users(self, key='name'):
        """
        return all users in database by key (default is name)
        :param key: str
        :return: list
        """
        response = self.read_query(f"SELECT {key} from users")
        if key == '*':
            return response
        return [item[0] for item in response]

    def get_user(self, value, key='name'):
        """
        get user by key-value pair
        :param value: str
        :param key: str
        :return: dict with all info for the matched user
        """

        usr = self.read_query(f"SELECT * FROM users WHERE {key}='{value}'")
        if usr:
            usr = usr[0]

        return {self.rows[i]: usr[i] for i in range(len(self.rows))}

    def delete_message(self, name, msg):
        """
        Delete message from messages table by user name and text
        :param name: str user_name
        :param msg: str text of message
        :return: int 0 if success -1 otherwise
        """
        user_id = self.read_query(f"SELECT id from users WHERE name = '{name}'")
        if user_id:
            user_id = user_id[0][0]
        else:
            print("[EXCEPTION] No user with that name")
        try:
            return self.execute_query("DELETE from messages WHERE user_id=? and text=?", params=(user_id, msg))
        except Error as e:
            print("[EXCEPTION]", e)

    def delete_user(self, name):
        try:
            self.execute_query(f"DELETE from users WHERE name=?", f"[OK] DELETED {name}", (name,))

        except Error as e:
            print("[EXCEPTION]", e)

    def get_messages(self):
        """
        return list of dict for all messages in database
        :return: list[] of dict {}
        """
        query = """
                SELECT
                    
                    users.name,
                    messages.text,
                    messages.time
                FROM
                    messages
                    INNER JOIN users ON users.id = messages.user_id
                """
        return [{'name': message[0], 'text': message[1], 'time':message[2]} for message in self.read_query(query)]

    def is_user(self, value, key='name'):
        if self.read_query(f"SELECT id from users WHERE {key} = '{value}'"):
            return True
        return False


if __name__ == '__main__':
    d = DataBase('test.db')
    for message in d.get_messages():
        print(f"{message['name']} said: {message['text']} at {message['time']}")

