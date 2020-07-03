from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.uix.label import Label
import rsa
import psycopg2
import bcrypt

Config.set('graphics', 'resizable', 1)
# Config.set('graphics', 'width', 300)
# Config.set('graphics', 'height', 600)
user_login = ''
user_id = ''
private_key = rsa.PrivateKey(1, 2, 3, 4, 5)
auto_fill_data_file = 'rem.rm'
private_key_file = 'priv_key.PEM'


def exception_handler(connect, cursor):
    try:
        cursor.close()
        connect.close()
    except Exception:
        pass


def pg_connect():
    try:
        con = psycopg2.connect(
            host="ec2-54-75-244-161.eu-west-1.compute.amazonaws.com",
            database="d8fi2kbfpchos",
            user="iutnqyyujjskrr",
            port="5432",
            password="45be3b8ccf0ce93d0e142ec546edaa8a067370f5c050b92b4c181730fb2c9814")
        cur = con.cursor()
        return con, cur
    except Exception:
        pass


def show_popup():
    layout = GridLayout(cols=1, padding=10)
    popupLabel = Label(text="Input error")
    closeButton = Button(text="OK")
    layout.add_widget(popupLabel)
    layout.add_widget(closeButton)
    popup = Popup(title='Error', content=layout, size_hint=(None, None), size=(250, 150))
    closeButton.bind(on_press=popup.dismiss)
    return popup


def check_input(password: str, log: str):
    popup = show_popup()
    if len(log) < 5:
        popup.open()
        return False
    if len(password) < 8:
        popup.open()
        return False
    for i in password:
        if ord(i) < 45 or ord(i) > 122:
            popup.open()
            return False
    for i in log:
        if ord(i) < 45 or ord(i) > 122:
            popup.open()
            return False
    return True


def check_password(cursor, log, pas):
    try:
        cursor.execute("SELECT password FROM users WHERE login='{0}'".format(log))
        res = cursor.fetchall()[0][0]
        hashed_password = res.encode('utf-8')
        if bcrypt.checkpw(pas, hashed_password):
            return "True"
        return "False"
    except IndexError:
        return "None"
    except Exception as e:
        pass


def get_id(cursor):
    global user_login
    try:
        cursor.execute("SELECT id FROM users WHERE login='{0}'".format(user_login))
        res = cursor.fetchall()
        return res[0][0]
    except Exception as e:
        pass


def get_user_id(user, cursor):
    try:
        cursor.execute("SELECT id FROM users WHERE login='{0}'".format(user))
        res = cursor.fetchall()
        return res[0][0]
    except IndexError:
        return None
    except Exception as e:
        pass


def get_user_nickname(user, cursor):
    try:
        cursor.execute("SELECT login FROM users WHERE id={0}".format(user))
        res = cursor.fetchall()
        return res[0][0]
    except IndexError:
        return None
    except Exception as e:
        pass


def get_private_key():
    try:
        global private_key
        with open(private_key_file, 'rb') as file:
            data = file.read()
        private_key = rsa.PrivateKey.load_pkcs1(data)
    except FileNotFoundError:
        pass


def regenerate_keys():
    global user_id
    connect, cursor = pg_connect()
    try:
        cursor.execute("UPDATE users SET pubkey='{0}' WHERE id={1}".format(keys_generation(), user_id))
        connect.commit()
        cursor.close()
        connect.close()
    except Exception:
        exception_handler(connect, cursor)


def keys_generation():
    global private_key
    try:
        (pubkey, privkey) = rsa.newkeys(512)
        pubkey = str(pubkey)[10:-1]
        with open(private_key_file, 'w') as file:
            file.write(privkey.save_pkcs1().decode('ascii'))
        private_key = privkey
        return pubkey
    except Exception:
        pass


def login(log, pas):
    global user_login
    global user_id
    connect, cursor = pg_connect()
    popup = show_popup()
    try:
        if len(log) == 0 or len(pas) == 0:
            popup.open()
            return
        res = check_password(cursor, log, pas.encode('utf-8'))
        if res == "False":
            cursor.close()
            connect.close()
            popup.open()
            return
        elif res == "None":
            cursor.close()
            connect.close()
            popup.open()
            return
        user_login = log
        user_id = get_id(cursor)
        get_private_key()
        cursor.close()
        connect.close()
        return True
    except Exception:
        exception_handler(connect, cursor)


def get_message(list_box):
    global user_id
    connect, cursor = pg_connect()
    try:
        cursor.execute("SELECT * FROM messages WHERE to_id={0}".format(user_id))
        res = cursor.fetchall()
        cursor.execute("DELETE FROM messages WHERE to_id={0}".format(user_id))
        connect.commit()
        for i in res:
            decrypt_msg = decrypt(i[2])
            nickname = get_user_nickname(i[0], cursor)
            content = '\n{0}: {1}'.format(nickname, decrypt_msg)
            list_box.text += content
        cursor.close()
        connect.close()
    except Exception as e:
        exception_handler(connect, cursor)


def send_message(to_id, msg):
    global user_id
    connect, cursor = pg_connect()
    popup = show_popup()
    try:
        if len(to_id) == 0 or len(msg) == 0:
            popup.open()
            cursor.close()
            connect.close()
            return
        for i in msg:
            if ord(i) < 32 or ord(i) > 1366:
                popup.open()
                cursor.close()
                connect.close()
                return
        to_id = int(to_id)
        cursor.execute("SELECT pubkey FROM users WHERE id={0}".format(to_id))
        res = cursor.fetchall()[0][0]
        encrypt_msg = encrypt(msg, res)
        cursor.execute("INSERT INTO messages VALUES ({0}, {1}, {2})".format(user_id, to_id, encrypt_msg))
        connect.commit()
        cursor.close()
        connect.close()
    except Exception:
        exception_handler(connect, cursor)


def encrypt(msg: str, pubkey):
    try:
        pubkey = pubkey.split(', ')
        pubkey = rsa.PublicKey(int(pubkey[0]), int(pubkey[1]))
        encrypt_message = rsa.encrypt(msg.encode('utf-8'), pubkey)
        encrypt_message = encrypt_message
        return psycopg2.Binary(encrypt_message)
    except Exception:
        pass


def decrypt(msg: bytes):
    global private_key
    try:
        decrypted_message = rsa.decrypt(msg, private_key)
        return decrypted_message.decode('utf-8')
    except Exception as e:
        pass


class DatabaseChat(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_log = TextInput()
        self.entry_pass = TextInput(password=True)
        self.al = AnchorLayout()
        self.bl = BoxLayout(orientation='vertical', size_hint=[.7, .15])
        self.bl2 = BoxLayout(orientation='vertical')
        self.bl_buttons = BoxLayout(orientation='horizontal')
        self.entry_msg = TextInput(size_hint=[.1, .05])
        self.entry_id = TextInput(size_hint=[.015, .05])
        self.msg_box = TextInput()

    def login(self, instance):
        if login(self.entry_log.text, self.entry_pass.text):
            self.al.remove_widget(self.bl)
            self.al.add_widget(self.msg_box)
            self.al.add_widget(self.bl2)
            get_message(self.msg_box)
            return self.al

    def send_message(self, instance):

        send_message(self.entry_id.text, self.entry_msg.text)
        self.entry_msg.text = ''
        # self.msg_box.text += '\n' + self.entry_msg.text

    def build(self):
        self.bl.add_widget(self.entry_log, self.entry_pass)
        self.bl.add_widget(self.entry_pass)
        self.bl.add_widget(Button(text='LOGIN', on_press=self.login))
        self.al.add_widget(self.bl)
        self.bl_buttons.add_widget(self.entry_id)
        self.bl_buttons.add_widget(self.entry_msg)
        self.bl2.add_widget(self.bl_buttons)
        self.bl2.add_widget(Button(text='SEND', on_press=self.send_message, size_hint=[.999, .05]))
        return self.al


if __name__ == "__main__":
    DatabaseChat().run()
