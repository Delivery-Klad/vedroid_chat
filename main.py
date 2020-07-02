from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.config import Config

Config.set('graphics', 'resizable', 1)
Config.set('graphics', 'width', 300)
Config.set('graphics', 'height', 600)


class DatabaseChat(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_log = TextInput()
        self.entry_pass = TextInput(password=True)
        self.al = AnchorLayout()
        self.bl = BoxLayout(orientation='vertical', size_hint=[.7, .2])

    def login(self, instance):
        print(self.entry_log.text)
        print(self.entry_pass.text)
        self.al.remove_widget(self.bl)

    def build(self):
        self.bl.add_widget(self.entry_log)
        self.bl.add_widget(self.entry_pass)
        self.bl.add_widget(Button(text='LOGIN', on_press=self.login))
        self.al.add_widget(self.bl)
        return self.al


if __name__ == "__main__":
    DatabaseChat().run()
