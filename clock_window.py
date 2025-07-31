
from kivy.config import Config

# Must be set before importing any Kivy modules
Config.set('graphics', 'resizable', '0')    # Enable resizing
Config.set('graphics', 'borderless', '0')   # Show window border

from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
import json
import os
from datetime import datetime
from logic.logic import create_session, clock_in
import threading

CACHE_FILE = "user_cache.json"
from dotenv import load_dotenv

load_dotenv()



clock_in_url = os.getenv('URL')


def load_user_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

user_cache = load_user_cache()

def on_clock_in_button_press():
    username = user_cache.get("username")
    password = user_cache.get("password")

    if not username or not password:
        print("No saved credentials found. Please login again.")
        # Optionally, show popup or navigate to login screen
        return

    def clock_in_task():
        try:
            session = create_session()

            data, duration, _ = clock_in(session, username, password, clock_in_url)
            print(f"✅ Clock-in succeeded in {duration:.2f}s: {data}")
            # Update UI, show success toast/dialog here

        except Exception as e:
            print(f"❌ Clock-in failed: {e}")
            # Show error dialog or toast in UI here

    threading.Thread(target=clock_in_task, daemon=True).start()



KV = """

ScreenManager:
    id: screen_manager

    MainScreen:
        name: "main"

    SettingsScreen:
        name: "settings"
        

<MainScreen@FloatLayout>:
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0.184, 0.184, 0.184, 0.7  # #2f2f2f
            Rectangle:
                pos: self.pos
                size: self.size

        MDBoxLayout:
            size_hint: 1, None
            height: dp(550)
            pos_hint: {"top": 1}
            padding: [dp(15), dp(15), dp(15), 0]
            radius: [20, 20, 20, 20]
            elevation: 12
            orientation: 'vertical'

            # PROFILE IMAGE
            FitImage:
                id: profile_image
                source: ""
                size_hint_y: None
                height: dp(340)
                radius: [30, 30, 40, 40]
                allow_stretch: True
                
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 0.95
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20, 20, 20, 20]


            # SPACING BELOW IMAGE
            Widget:
                size_hint_y: None
                height: dp(20)

            # NAME + BODY + BUTTON WRAPPER
            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(16)
                padding: [dp(18), dp(13), dp(24), 0]

                # NAME + TICK
                MDBoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(6)
                    pos_hint: {"left": 0.9}

                    MDLabel:
                        id: user_name
                        text: ""
                        theme_text_color: "Custom"
                        text_color: (1, 1, 1, 0.9)
                        adaptive_size: True
                        bold:True
                        font_size: "30sp"
                        

                    MDIcon:
                        icon: "check-decagram"
                        theme_text_color: "Custom"
                        text_color: (0.113, 0.631, 0.949, 0.89)
                        font_size: "25sp"
                        size_hint: None, None
                        size: self.texture_size
                        pos_hint: {"center_y": 0.45}

                # MOTIVATION LINE
                MDLabel:
                    text: "Driven by code, united by purpose and passion."
                    theme_text_color: "Secondary"
                    font_style: "Body1"
                    font_size: "20sp"
                    halign: "left"
                    size_hint_y: None
                    height: self.texture_size[1]
                    
                # CLOCK IN ROW
                MDGridLayout:
                    cols: 2
                    spacing: dp(12)
                    size_hint_y: None
                    height: dp(50)
                

                    # CLOCK IN BUTTON
                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: [0, dp(10)]  # Top and bottom padding

                        MDFillRoundFlatIconButton:
                            id: check_in_button
                            text: "Clock In"
                            icon: "clock-outline"
                            size_hint: None, None
                            width: dp(240)
                            height: dp(50)
                            font_size: "15sp"
                            padding: [dp(30),dp(10),dp(30),dp(10)]  # Top and bottom padding
                            on_release: (app.on_clock_in_button_press(), app.start_action())

                            # Colors - soft whiteish-gre
                            md_bg_color: 0.145, 0.827, 0.4, 0.72
                            text_color: 1,1,1, 0.95
                            icon_color:  1,1,1, 0.95
                            blod:True
                            theme_text_color: "Custom"

                            # Position
                            pos_hint: {"center_x": 0.53}

                    # STATUS COLUMN
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(5)
                        size_hint_y: None
                        height: dp(50)
                        #pos_hint: {"y": 1}
                        padding: [dp(45), 0, 0, 0]

                        # CLOCK ICON
                        MDIcon:
                            icon: "watch"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 0.8
                            font_size: "29sp"
                            size_hint: None, None
                            size: dp(24), dp(24)
                            pos_hint: {"y": 0.3}

                        # CLOCK-IN TIME LABEL
                        MDLabel:
                            id: timer_label
                            text: ""
                            theme_text_color: "Secondary"
                            font_style: "Body1"
                            font_size: "14sp"
                            text_color: 0.3, 0.3, 0.3, 1
                            size_hint_y: None
                            adaptive_size: True
                            height: self.texture_size[1]
                            valign: "middle"
                            pos_hint: {"y": 0.4}
                            
                            
                            
<SettingsScreen@BoxLayout>:
    orientation: "vertical"
    MDLabel:
        text: "Settings"
        halign: "center"
        font_style: "H4"
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1

    MDRaisedButton:
        text: "Back to Main"
        pos_hint: {"center_x": 0.5}
        on_release: app.root.current = "main"
"""

class MyWidget(BoxLayout):
    pass

class MsgApp(MDApp):

    def on_clock_in_button_press(self):
        on_clock_in_button_press()

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_seconds = 0
        self.timer_event = None
        self.clocked_in = False  

    def build(self):
        self.title = ' ' 
        Window.size = (350, 580)
        Window.minimum_size = Window.size
        Window.top = 50
        Window.left = 990
        Window.title = "MCRM"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        Window.clearcolor = (0, 0, 0, 0)
        #Window.opacity = 0.9
        return Builder.load_string(KV)
    
    
    
    def update_clock_label(self, dt):
        current_time = datetime.now().strftime("%I:%M %p")  # 12-hour format
        self.root.ids.timer_label.text = current_time



    def on_start(self):
        try:
            if os.path.exists("user_cache.json"):
                with open("user_cache.json", "r") as file:
                    user_data = json.load(file)

                firstname = user_data.get("firstname", "User").title()
                self.root.ids.user_name.text = firstname
                self.root.ids.profile_image.source = user_data.get("profile_thumb", "Wel.png")
        except Exception as e:
            print("Error loading cache:", e)

        # Start the system clock display
        self.clock_event = Clock.schedule_interval(self.update_clock_label, 1)
        
        
        
    def update_timer(self, dt):
        self.timer_seconds += 1
        hours, remainder = divmod(self.timer_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.root.ids.timer_label.text = time_str





    def start_action(self):
        btn = self.root.ids.check_in_button

        if not self.clocked_in:
            # Switching to red state (Clocked In)
            if self.clock_event:
                self.clock_event.cancel()
                self.clock_event = None

            self.timer_seconds = 0
            self.update_clock_label(0)

            if self.timer_event is None:
                self.timer_event = Clock.schedule_interval(self.update_timer, 1)

            # Change button appearance for Clock Out
            btn.text = "Clock Out"
            btn.icon = "close"  # Cancel icon
            btn.icon_size = "15sp"
            btn.md_bg_color = (1, 0.2, 0.2, 0.8)  # Red
            btn.text_color = (1, 1, 1, 1)
            btn.icon_color = (1, 1, 1, 1)

            # Disable button manually by ignoring input, but keep color red
            btn.disabled = True

            # Schedule to enable after 5 seconds
            Clock.schedule_once(lambda dt: self.enable_button(btn), 5)

            self.clocked_in = True

        else:
            # Switching back to normal state (Clock In)
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None

            self.timer_seconds = 0
            self.update_clock_label(0)

            self.clock_event = Clock.schedule_interval(self.update_clock_label, 1)

            btn.text = "Clock In"
            btn.icon = "clock-outline"
            btn.icon_size = "15sp"
            btn.md_bg_color = (0.145, 0.827, 0.4, 0.75)  # Original grey md_bg_color: 
            btn.text_color = (0.1, 0.1, 0.1, 1)
            btn.icon_color = (0.1, 0.1, 0.1, 1)

            btn.disabled = False  # Enable immediately

            self.clocked_in = False


    def enable_button(self, btn):
        # Enable the button after 5 seconds but keep the red color if clocked in
        btn.disabled = False
        # Just to be safe, reset colors to red if still clocked in
        if self.clocked_in:
            btn.md_bg_color = (1, 0.2, 0.2, 1)
            btn.text_color = (1, 1, 1, 1)
            btn.icon_color = (1, 1, 1, 1)




    def close_application(self):
        self.stop()

    def minimize_window(self):
        Window.minimize()