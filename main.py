from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.uix.label import Label
import os
import psycopg2
import bcrypt

Config.set('graphics', 'resizable', 1)
Config.set('graphics', 'width', 300)
Config.set('graphics', 'height', 600)
user_login = ''
user_id = ''
auto_fill_data_file = 'rem.rm'
private_key_file = 'priv_key.PEM'


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
        self.al.remove_widget(self.bl)
        self.al.add_widget(self.msg_box)
        self.al.add_widget(self.bl2)
        return self.al

    def send_message(self, instance):
        self.entry_msg.text += '\n' + self.entry_msg.text
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
