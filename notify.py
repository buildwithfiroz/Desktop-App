#Notify.py

from datetime import datetime
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.config import Config 
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel

KV = '''
BoxLayout:
    orientation: 'vertical'

    MDFloatLayout:
        MDIconButton:
            icon: "close-circle"
            theme_text_color: "Custom"
            icon_size: "20sp"
            text_color: 1, 0, 0, 1
            pos_hint: {'center_x': 0.06, 'center_y': 0.8}
            opacity: 0.9
            on_release: app.close_application()
        
        AsyncImage:
            id: user_pic
            source: "src/img/logo.png"
            size_hint: None, None
            size: "120dp", "120dp"
            pos_hint: {'center_x': 0.8, 'center_y': 0.5}

        MDLabel:
            text: 'Assalam Walekum,'
            theme_text_color: 'Custom'
            opacity: 0.8
            text_color: 1, 1, 1, 0.8
            font_style: 'H6'
            pos_hint: {'center_x': 0.6 ,  'center_y': 0.8}

        MDLabel:
            id: user_name
            text: 'Wans'
            pos_hint: {'center_x': 0.6 ,  'center_y': 0.69}
            theme_text_color: 'Custom'
            text_color: 0.5, 0.5, 0.5, 0.5
            font_style: 'Body2'
            
        MDLabel:
            text: "[b] Let[color=#673AB7] 's Work To[/color]gether ! [/b]"
            pos_hint: {'center_x': 0.58, 'center_y': 0.45}
            markup: True
            theme_text_color: 'Custom'
            text_color: 0.5, 0.5, 0.5, 0.5
            font_style: 'H5'
            
        MDLabel:
            text: " Logged-In : "
            pos_hint: {'center_x': 0.59, 'center_y': 0.2}
            markup: True
            theme_text_color: 'Custom'
            text_color: 0.5, 0.5, 0.5, 0.5
            font_name: "Nova"
            font_style: 'Body2'
            
        MDLabel:
            id: time_label
            text: ""
            pos_hint: {'center_x': 0.76, 'center_y': 0.2}
            theme_text_color: 'Custom'
            text_color:  1, 1, 1, 0.3
            font_style: 'Body2'
'''

class MsgApp(MDApp):
    current_time = StringProperty()
    
    def build(self):
        Window.size = [450, 150]
        Window.minimum_size = Window.size
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        # LabelBase.register(name='Nova', fn_regular='./Font/NovaSquare-Regular.ttf')

        sound = SoundLoader.load('./src/audio/ting.mp3')
        if sound:
            sound.play()

        screen = Builder.load_string(KV)

        # Set static username
        screen.ids.user_name.text = "Wans"

        # Set current time
        current_time = datetime.now().strftime("%I:%M:%S %p")
        screen.ids.time_label.text = current_time

        return screen

    def close_application(self):
        self.stop()

    def on_request_close(self):
        popup = Popup(title='Logout Required',
                      content=Label(text='Please log out before closing the window.'),
                      size_hint=(None, None), size=(300, 200))
        popup.open()
        return True

if __name__ == '__main__':
    MsgApp().run()
