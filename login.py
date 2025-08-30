from kivy.config import Config

# Must be set before importing any Kivy modules
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'borderless', '0')
Config.set('kivy','window_icon','logo.ico')

# login.py
import os
import sys
import time
import json
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from threading import Thread
from multiprocessing import Process, freeze_support
from clock_window import MsgApp  # Main clock app
import subprocess
from PIL import Image
from io import BytesIO
import requests
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from datetime import datetime
from dotenv import load_dotenv
from kivymd.toast import toast
import requests
import time
import socket
import logging
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime
import os 
from datetime import datetime
os.environ['KIVY_NO_CONSOLELOG'] = '1'  # No console output
os.environ['KIVY_NO_FILELOG'] = '1'     # No log file
os.environ['KIVY_LOG_MODE'] = 'PYTHON'  # Skip Kivy's handlers entirely
load_dotenv()

domain = os.getenv('ENDPOINT')



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


            
def run_notify_popup(firstname, profile_thumb, checkin_time, job_position):

    # Clear the popup flag
    cache_data = load_user_cache()
    cache_data["popup_needed"] = False
    save_user_cache(cache_data)

    # Ensure job_position is not None
    if job_position is None:
        job_position = "N/A"

    # Start the popup process
    subprocess.Popen(
        [sys.executable, os.path.abspath("notify_popup.py"),
         firstname, profile_thumb, checkin_time, job_position],
        shell=False
    )

        
def create_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"HEAD", "GET", "OPTIONS", "POST"}
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers['Expect'] = ''
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
    return session


def warm_up_connection(session: requests.Session, base_url: str, timeout: float = 2.0):
    try:
        response = session.head(base_url, timeout=timeout)
        response.raise_for_status()
        logger.info("Warm-up connection succeeded (HEAD)")
    except requests.RequestException:
        try:
            response = session.get(base_url, timeout=timeout)
            response.raise_for_status()
            logger.info("Warm-up connection succeeded (GET)")
        except Exception as e:
            logger.warning(f"Warm-up connection failed: {e}")


def login_optimized(session: requests.Session, username: str, password: str, url: str, timeout: float = 5.0):
    payload = {"email": username, "password": password}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate'
    }

    start_time = time.perf_counter()
    response = session.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    elapsed = time.perf_counter() - start_time

    data = response.json()
    if not data.get("status", False):
        raise ValueError(f"Login failed: {data.get('message', 'Unknown error')}")

    return data, elapsed, response.text


def logic_main(url: str, username: str, password: str):
    try:
        socket.gethostbyname(f"{domain}")
    except socket.gaierror as e:
        logger.error(f"DNS resolution failed: {e}")
        return None

    session = create_session()
    logger.info("⏱️ Warming up connection...")
    warm_up_connection(session, f"https://{domain}/")

    try:
        data, duration, _ = login_optimized(session, username, password, url)
        logger.info(f"✅ Login succeeded in {duration:.4f} seconds.")

        # Extracting values from response
        firstname = data.get("firstname", "")
        lastname = data.get("lastname", "")
        full_name = f"{firstname} {lastname}".strip()
        thumb_url = data.get("profile_thumb")
        job_position = data.get("job_position")

        checkin_time_str = data.get("checkin", {}).get("datetime")
        checkin_time_fmt = None

        if checkin_time_str:
            try:
                dt_obj = datetime.strptime(checkin_time_str, "%Y-%m-%d %H:%M:%S")
                checkin_time_fmt = dt_obj.strftime("%I:%M %p")
            except ValueError:
                logger.warning("Invalid check-in time format")

        return {
            "full_name": full_name,
            "profile_thumb": thumb_url,
            "job_position": job_position,
            "checkin_time": checkin_time_fmt,
            "duration": duration
        }

    except Exception as e:
        logger.error(f"❌ Login attempt failed: {e}")
        return None




load_dotenv()

url = os.getenv('URL')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

SPLASH_HONE = """
#:import Animation kivy.animation.Animation

MDScreen:
    name: 'intro'

    MDFloatLayout:

        MDLabel:
            id: label1
            text: 'WELCOME'
            theme_text_color: 'Custom'
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            text_color: 0.5, 0.5, 0.5, 1
            bold: True
            adaptive_size: True
            font_size: "60sp"
            opacity: 1

        # MDIconButton for logo
        BoxLayout:
            orientation: 'vertical'
            size_hint: None, None
            size: self.minimum_width, self.minimum_height
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            adaptive_size: True


            # MDIconButton for logo
            MDIconButton:
                id: my_icon1
                icon_size: "110sp"
                icon: "src/img/logo.png"
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                theme_text_color: "Custom"
                on_release: app.root.current = 'Login'
                opacity: 0

            # Text label 'NEXGENO'
            MDLabel:
                id: label2
                text: 'NEXGENO'
                adaptive_size: True
                theme_text_color: 'Custom'
                text_color: 0.5, 0.5, 0.5, 1
                bold: True
                font_size: "60sp"
                opacity: 0

            # Text label for 'TECHNOLOGY PRIVATE LIMITED'
            MDLabel:
                id: label3
                text: 'TECHNOLOGY PRIVATE LIMITED'
                theme_text_color: 'Custom'
                adaptive_size: True
                text_color: 0.5, 0.5, 0.5, 1
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                font_style: 'Body1'
                font_size: "10sp"
                opacity: 0

"""

KV = """


<LoaderOverlay@FloatLayout>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.4
        Rectangle:
            pos: self.pos
            size: self.size

    MDProgressBar:
        id: loader_overlay
        size_hint: None, None
        size: "410dp", "10dp"  # Adjust size according to button size
        pos_hint: {"center_x": 0.22, "center_y": 0.3}
        color: app.theme_cls.primary_color  # Set color
        max: 100  # Maximum value for the progress
        value: 0  # Start with 0 progress value
        orientation: 'horizontal'  # Horizontal progress bar

MDScreen:
    name: 'Login'

    FloatLayout:
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1  # Solid premium black
            Rectangle:
                pos: self.pos
                size: self.size

            # Overlay subtle noise texture
            Color:
                rgba: 1, 1, 1, 0.1  # Very subtle white noise
            Rectangle:
                source: "src/img/blur.jpg"  # Add a seamless noise image here
                pos: self.pos
                size: self.size


        LoaderOverlay:
            id: loader_overlay
            opacity: 0
            disabled: True

        BoxLayout:
            orientation: 'horizontal'
            spacing: dp(20)
            padding: dp(40)

            # Left Section - Login Form
            MDFloatLayout:
                size_hint_x: 0.5

                # Logo and App Name
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: None, None
                    size: dp(180), dp(40)
                    pos_hint: {"center_x": 0.23, "center_y": 0.85}
                    spacing: dp(10)

                    FloatLayout:
                        size_hint: None, None
                        size: dp(44), dp(44)
                        
                        FitImage:
                            source: "src/img/logo.png"
                            size_hint: None, None
                            size: dp(44), dp(44)
                            pos_hint: {"center_x": 0.5, "center_y": 0.5}
                            allow_stretch: True
                            keep_ratio: True

                    # MDLabel:
                    #     text: "Nexgeno"
                    #     theme_text_color: 'Custom'
                    #     text_color: 1, 1, 1, 1
                    #     font_size: "10sp"
                    #     valign: 'middle'
                    #     bold: True


                # Title
                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(0)
                    size_hint: None, None
                    size: self.minimum_size
                    pos_hint: {"center_x": 0.25, "center_y": 0.75}  # Adjust vertical position as needed

                    MDLabel:
                        text: "Welcome,"
                        font_style: "H3"  # Equivalent to H2 feel
                        theme_text_color: "Custom"
                        adaptive_size: True
                        text_color: 1, 1, 1, 0.8
                        halign: "left"
                        bold: True

                    MDLabel:
                        text: "To Nexgeno"
                        adaptive_size: True
                        font_size: "27sp"
                        theme_text_color: "Secondary"
                        halign: "left"


                # Login Form
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 0.65, None
                    height: self.minimum_height
                    spacing: dp(20)
                    pos_hint: {"center_x": 0.41, "center_y": 0.4}

                    # Username
                    MDTextField:
                        id: user
                        icon_left: "account"
                        hint_text: "Username"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(50)
                        on_text: app.check_input_length()
                        focus: True 

                    # Password + Eye Toggle
                    RelativeLayout:
                        size_hint_y: None
                        height: dp(50)

                        MDTextField:
                            id: pass_s
                            hint_text: "Password"
                            icon_left: "key"
                            mode: "rectangle"
                            size_hint: 1, None
                            height: dp(50)
                            password: True
                            on_text_validate: app.on_password_enter()
                            on_text: app.check_input_length()
                            multiline: False

                        MDIconButton:
                            id: icon_button
                            icon: "eye-off"
                            pos_hint: {"center_y": 0.5}
                            size_hint: None, None
                            size: dp(24), dp(24)
                            on_release:
                                pass_s.password = not pass_s.password
                                icon_button.icon = "eye-off" if pass_s.password else "eye"
                            x: pass_s.right - self.width - dp(10)

                    

                    # Remember Me
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint: 1, None
                        height: dp(30)
                        spacing: dp(10)
                        padding: [0, dp(3)]  # Adjust vertical padding as needed


                        MDCheckbox:
                            id: remember_me_checkbox
                            size_hint: None, None
                            size: dp(24), dp(24)
                            active: True  # Default checked
                            on_active: app.update_remember_me(self.active)

                        MDLabel:
                            text: "Remember Me"
                            font_size: "14sp"
                            theme_text_color: "Secondary"
                            valign: "middle"
                            pos_hint: {"top": 1}
                            on_touch_down:
                                if self.collide_point(*args[1].pos): \
                                root.ids.remember_me_checkbox.active = not root.ids.remember_me_checkbox.active


                    MDLabel:
                        id: retry_label
                        text: ""
                        theme_text_color: "Error"
                        halign: "center"
                        markup: True
                        font_style: "Subtitle1"
                        opacity: 0  # Hidden by default
                        pos_hint: {"top": 0.9}

                    # Login Button
                    MDRaisedButton:
                        id: login_button
                        text: "Login"
                        disabled: True
                        on_release: app.check_credentials()
                        size_hint: 1, None

                # Footer: Labels side by side — inside form container
                BoxLayout:
                    size_hint_y: None
                    pos_hint: {"center_x": 0.59, "center_y": 0.1}

                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint: None, None
                        spacing: dp(6)
                        size: self.minimum_size
                        pos_hint: {"center_x": 0.5}

                        MDLabel:
                            text: 'Not a member yet?'
                            font_size: "12sp"
                            opacity: 0.6
                            theme_text_color: "Secondary"
                            size_hint_x: None
                            adaptive_size: True
                            width: self.texture_size[0]

                        MDLabel:
                            text: 'Contact Admin'
                            font_size: "12sp"
                            opacity: 0.8
                            theme_text_color: 'Custom'
                            adaptive_size: True
                            text_color: app.theme_cls.primary_color
                            size_hint_x: None
                            width: self.texture_size[0]

            # Right Section - Image
            FloatLayout:
                size_hint_x: 0.5
                padding: [0, dp(30), dp(30), dp(30)]

                FitImage:
                    source: "src/img/login_page.png"
                    allow_stretch: True
                    keep_ratio: True
                    size_hint: 1.05, 1.05
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    radius: [30, 30, 30, 30]


"""


notify = """
FloatLayout:
    canvas.before:
        Color:
            rgba: 0.184, 0.184, 0.184, 0.7  # #2f2f2f
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        
       

        MDFloatLayout:
            # Time Label - Top Right
            MDLabel:
                id: time_label
                text: "12:45 PM"  # This will be dynamic
                halign: 'right'
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.6
                font_size: "12sp"
                pos_hint: {'right': 0.95, 'top': 1.12}
                
            MDIconButton:
                icon: "close-circle"
                theme_text_color: "Custom"
                icon_size: "20sp"
                text_color: 1, 0, 0, 1
                pos_hint: {'center_x': 0.05, 'center_y': 0.8}
                opacity: 0.9
                on_release: app.close_application()

            # Horizontal box to arrange image and user info side by side
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint: None, None
                size: "300dp", "150dp"
                padding: "20dp", "20dp"
                spacing: "15dp"
                pos_hint: {"right": 0.79, "top": 1.3}

                # User Image
                FitImage:
                    id: user_pic
                    source: ""
                    size_hint: None, None
                    size: "70dp", "70dp"
                    radius: "50dp"
                    allow_stretch: True
                    pos_hint: {"right": 0.9, "top": 0.8}


                            # User Text Info (vertical box)
                            # User Text Info (vertical box)
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    size_hint_y: None
                    height: self.minimum_height
                    pos_hint: {"top": 0.69}

                    # Name + Blue Tick (horizontal)
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(6)

                        MDLabel:
                            id: user_name
                            text: "Firoz Shaikh"
                            adaptive_size: True
                            font_size: "18sp"
                            bold: True

                        MDIcon:
                            icon: "check-decagram"
                            theme_text_color: "Custom"
                            text_color: (0.113, 0.631, 0.949, 0.89)
                            font_size: "15sp"
                            size_hint: None, None
                            size: self.texture_size
                            valign: "middle"
                            pos_hint: {"top": 0.9}

                    # Position label
                    MDLabel:
                        id: user_position 
                        text: "Head of AI"
                        theme_text_color: 'Custom'
                        text_color: 1, 1, 1, 0.8
                        font_style: 'Caption'
                        font_size: "13sp"
                        adaptive_size: True
"""



def update_clock_in_status(user_cache, clocked_in=True):
    user_cache["clocked_in"] = clocked_in
    user_cache["clock_in_time"] = datetime.now().isoformat()
    save_user_cache(user_cache)

def update_login_log(user_cache):
    today_str = datetime.now().strftime("%Y-%m-%d")
    logins = user_cache.get("logins", [])
    
    # Update today's login count or append new
    for entry in logins:
        if entry.get("date") == today_str:
            entry["count"] += 1
            break
    else:
        logins.append({"date": today_str, "count": 1})

    user_cache["logins"] = logins

    # Make sure clock_in_time & clocked_in are preserved or updated accordingly
    if "clocked_in" not in user_cache:
        user_cache["clocked_in"] = False
    if "clock_in_time" not in user_cache:
        user_cache["clock_in_time"] = ""

    save_user_cache(user_cache)



def download_and_optimize_image(url: str, save_path: str, quality: int = 85) -> bool:
    try:
        headers = {
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",

        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Verify content is actually an image
        if 'image' not in response.headers.get('Content-Type', ''):
            raise ValueError("Response is not an image")

        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.save(save_path, format="JPEG", optimize=True, quality=quality)
        return True
        
    except Exception as e:
        print(f"[❌ Image Download Error] URL: {url} | Error: {e}")
        return False



CACHE_FILE = "user_cache.json"



def load_user_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_user_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=4)


class NotifyPopupApp(MDApp):
    
    def __init__(self, firstname="User", profile_thumb="tmp/tester_nexgeno_in_thumb.jpeg", checkin_time="N/A", job_position="Staff", **kwargs):
        super().__init__(**kwargs)
        self.firstname = firstname
        self.profile_thumb = profile_thumb
        self.checkin_time = checkin_time
        self.job_position = job_position  # ✅ Added


    def build(self):
        Window.size = [400, 100]
        self.title = ''
        Window.top = 50
        Window.left = 850
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        

        screen = Builder.load_string(notify)
        
        screen.ids.user_name.text = self.firstname
        screen.ids.user_pic.source = self.profile_thumb
        screen.ids.time_label.text = self.checkin_time
        screen.ids.user_position.text = self.job_position

        # Close the app after 7 seconds of inactivity
        Clock.schedule_once(self.close_application, 5)
        
        return screen
    
    def close_application(self, dt=None):
        """Close the application."""
        self.stop()




    


class CustomScreen(Screen):
    def on_success_login(self):
        self.ids.login_button.text = ""
        self.ids.login_button.disabled = True

    def load_next_screen(self):
        self.remove_widget(self.children[-1])
        self.ids.login_button.text = "Login"
        self.ids.login_button.disabled = False


class Notify(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.failed_login_attempts = 0
        self.locked_out = False
        self.dialog_open = False 

        
    def on_password_enter(self):
        if self.locked_out:
            return

        screen = self.sm.get_screen('Login')
        user_field = screen.ids.user
        pass_field = screen.ids.pass_s

        username = user_field.text.strip()
        password = pass_field.text.strip()

        if len(username) >= 3 and len(password) >= 3:
            self.check_credentials()

    
    def update_remember_me(self, remember):
        """Update the remember me state in the UI and cache"""
        screen = self.sm.get_screen('Login')
        if screen:
            screen.ids.remember_me_checkbox.active = remember
            # Update cache immediately when checkbox changes
            cache_data = load_user_cache()
            cache_data["remember_me"] = remember
            save_user_cache(cache_data)
            
            
    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        screen = self.sm.get_screen('Login')
        user_field = screen.ids.user
        pass_field = screen.ids.pass_s
        login_button = screen.ids.login_button

        if key == 9:  # Tab key
            if user_field.focus:
                user_field.focus = False
                pass_field.focus = True
                return True
            elif pass_field.focus:
                pass_field.focus = False
                user_field.focus = True
                return True

        elif key == 13:  # Enter key
            # If dialog is open, send enter to dialog's OK button
            if self.dialog_open:
                if hasattr(self, 'dialog') and self.dialog:
                    # Simulate OK button press on Enter
                    for btn in self.dialog.buttons:
                        btn.trigger_action(duration=0)
                    return True

            # Block login if locked out or button invisible
            if self.locked_out or login_button.opacity == 0:
                return True  # ignore enter key

            username = user_field.text.strip()
            password = pass_field.text.strip()

            if pass_field.focus and len(username) >= 3 and len(password) >= 3:
                self.check_credentials()
                return True

        return False




            
            
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        Window.borderless = True
        Window.fullscreen = 'auto'
        
        Window.bind(on_key_down=self.on_key_down)

        # Preload sounds once
        self.error_sound = SoundLoader.load(resource_path('./src/audio/delete.mp3')) or None

        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))

        self.sm.add_widget(Builder.load_string(SPLASH_HONE))
        self.sm.add_widget(Builder.load_string(KV))
        return self.sm
    
    def update_loader_progress(self, increment=10):
        # This method will update the progress bar based on the increment value
        login_screen = self.sm.get_screen('Login')
        loader = login_screen.ids.loader_overlay  # This is the LoaderOverlay widget

        if loader and hasattr(loader, 'ids'):
            progress_bar = loader.ids.get('loader_overlay')  # Get the MDProgressBar inside the overlay
            if progress_bar:
                # Update the progress bar value with the increment
                progress_bar.value += increment
                
                # If the progress reaches 100%, reset the progress bar to 0 and stop the progress simulation
                if progress_bar.value >= progress_bar.max:
                    progress_bar.value = 0  # Reset the progress bar to 0
                    self.hide_loader()  # Hide loader after completion
                    return False  # Return False to stop progress simulation
        return True
    


    def show_loader(self):
        login_screen = self.sm.get_screen("Login")
        overlay = login_screen.ids.get("loader_overlay")
        if overlay:
            overlay.disabled = False
            Animation(opacity=1, duration=0.3).start(overlay)
            
            

    def hide_loader(self):
        login_screen = self.sm.get_screen("Login")
        overlay = login_screen.ids.get("loader_overlay")
        if overlay:
            anim = Animation(opacity=0, duration=0.3)
            anim.bind(on_complete=lambda *x: setattr(overlay, "disabled", True))
            anim.start(overlay)

    def dismiss_dialog(self, instance):
        if hasattr(self, "dialog") and self.dialog:
            self.dialog.dismiss()
            self.dialog = None

    def on_start(self):
    # Load remember me state from cache
        cache_data = load_user_cache()
        if "remember_me" in cache_data:
            self.update_remember_me(cache_data["remember_me"])
        self.start_intro_animation()

    def start_intro_animation(self):
        try:
            screen = self.sm.get_screen('intro')
            label1 = screen.ids.label1
            icon1 = screen.ids.my_icon1
            label2 = screen.ids.label2
            label3 = screen.ids.label3

            anim_label1 = Animation(opacity=1, duration=3)
            anim_label1.bind(on_complete=lambda *args: self.hide_and_show(label1, icon1, label2, label3))
            anim_label1.start(label1)
        except Exception as e:
            print(f"[Intro Animation Error] {e}")

    def hide_and_show(self, label1, icon1, label2, label3):
        Animation(opacity=0, duration=1).start(label1)
        Animation(opacity=0, duration=1).start(icon1)
        Animation(opacity=0, duration=1).start(label2)
        Animation(opacity=0, duration=1).start(label3)
        Clock.schedule_once(lambda dt: self.show_and_redirect(icon1, label2, label3), 3)

    def show_and_redirect(self, icon1, label2, label3):
        Animation(opacity=1, duration=1).start(icon1)
        Animation(opacity=1, duration=1).start(label2)
        Animation(opacity=1, duration=1).start(label3)
        Clock.schedule_once(lambda dt: self.redirect_to_login(), 3)

    def redirect_to_login(self):
        self.sm.transition = FadeTransition(duration=0.5)
        self.sm.current = 'Login'
        Clock.schedule_once(lambda dt: setattr(self.sm, 'transition', NoTransition()), 3)

    def check_input_length(self):
        screen = self.sm.get_screen('Login')
        if screen:
            username = screen.ids.user.text
            password = screen.ids.pass_s.text
            screen.ids.login_button.disabled = len(username) < 3 or len(password) < 3

  

    def login_success_ui(self, data):
        

            
        firstname = data.get("full_name", "User")  # Updated to full name
        job_position = data.get("job_position", "Staff")  # ✅ Add this line
        profile_thumb_url = data.get("profile_thumb", resource_path("src\\img\\logo.png"))
        checkin_time = data.get("checkin_time", "N/A")


        screen = self.sm.get_screen('Login')
        username = screen.ids.user.text
        password = screen.ids.pass_s.text

        # Save optimized image path
        local_img_path = f"./tmp/{username.replace('@', '_').replace('.', '_')}_thumb.jpg"
        os.makedirs("tmp", exist_ok=True)

        def finalize_and_launch_app(img_path):
            remember_me = screen.ids.remember_me_checkbox.active
            cache_data = {
                "logged_in": True,
                "popup_shown": False,
                "popup_needed": True,
                "firstname": firstname,
                "job_position": job_position,
                "profile_thumb": img_path,
                "checkin_time": checkin_time,
                "username": username if remember_me else "",
                "password": password if remember_me else "",
                "remember_me": remember_me
            }
            update_clock_in_status(cache_data, clocked_in=True)
            update_login_log(cache_data)
            save_user_cache(cache_data)


            # Exit current app
            self.stop()

        def background_image_worker():
            print(f"[🔁 Downloading profile image from: {profile_thumb_url}]")
            if download_and_optimize_image(profile_thumb_url, local_img_path):
                print("[✅ Image Downloaded]")
                img_path = local_img_path
            else:
                print("[⚠️ Falling back to default image]")
                img_path = resource_path("src\\img\\logo.png")
            Clock.schedule_once(lambda dt: finalize_and_launch_app(img_path), 0)


        # 🔄 Start background image download
        Thread(target=background_image_worker, daemon=True).start()



    
    def check_credentials(self):
        screen = self.sm.get_screen('Login')
        login_button = screen.ids.login_button
        login_button.disabled = True
        login_button.opacity = 0
        self.show_loader()

        username = screen.ids.user.text
        password = screen.ids.pass_s.text

        start_time = time.time()

        def update_progress_simulation(dt):
            elapsed_time = time.time() - start_time
            total_time = 5
            progress_percentage = (elapsed_time / total_time) * 100
            progress_percentage = min(progress_percentage, 100)
            if not self.update_loader_progress(increment=progress_percentage):
                return False
            return True

        update_progress_event = Clock.schedule_interval(update_progress_simulation, 0.1)

        def on_login_success(result_data):
            from kivymd.toast import toast
            toast(f"Login successful in {result_data.get('duration', 0):.2f}s")
            self.failed_login_attempts = 0  # Reset counter on success
            login_button.opacity = 1
            login_button.disabled = False
            self.hide_loader()
            self.login_success_ui(result_data)
            Clock.unschedule(update_progress_event)
            
        

        def on_login_error(e):
            print(f"Login failed: {str(e)}")
            if self.error_sound:
                self.error_sound.play()

            screen = self.sm.get_screen('Login')
            login_button = screen.ids.login_button
            retry_label = screen.ids.retry_label  # ✅ Reference to retry label

            self.failed_login_attempts += 1

            def show_error_after_delay(dt):
                self.locked_out = False
                login_button.disabled = False
                login_button.opacity = 1
                retry_label.text = ""
                retry_label.opacity = 0
                self.hide_loader()
                self.show_error_dialog("unauthorized")
                Clock.unschedule(update_progress_event)

            def start_retry_countdown(seconds=10):  # ✅ Countdown logic
                retry_label.opacity = 1
                retry_label.text = f"[color=#FF0000]Try again in {seconds} seconds[/color]"
                login_button.disabled = True
                login_button.opacity = 0

                def update_label(dt):
                    nonlocal seconds
                    seconds -= 1
                    if seconds > 0:
                        retry_label.text = f"[color=#FF0000]Try again in {seconds} seconds[/color]"
                    else:
                        retry_label.opacity = 0
                        login_button.disabled = False
                        login_button.opacity = 1
                        return False  # Stop the Clock
                    return True

                Clock.schedule_interval(update_label, 1)

            if self.failed_login_attempts > 3:
                self.locked_out = True
                toast("Please wait 10 seconds before trying again.")
                login_button.disabled = True
                login_button.opacity = 0

                # Reset progress bar if any
                loader = screen.ids.get("loader_overlay")
                if loader and hasattr(loader, 'ids'):
                    progress_bar = loader.ids.get('loader_overlay')
                    if progress_bar:
                        progress_bar.value = 0

                Clock.unschedule(update_progress_event)
                start_retry_countdown(10)  # ✅ Start countdown
            else:
                show_error_after_delay(0)


        def login_thread():
            try:
                result_data = logic_main(url, username, password)
                if not result_data:
                    raise Exception("Login failed: No data returned")
                Clock.schedule_once(lambda dt: on_login_success(result_data), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt, err=e: on_login_error(err), 0)

        Thread(target=login_thread, daemon=True).start()



    def show_error_dialog(self, reason="unknown"):
        error_messages = {
            "unauthorized": "Incorrect username or password. Please try again.",
            "dns": "Could not reach server. Check your internet connection.",
            "http_error": "Server error occurred. Try again later.",
            "unknown": "Login failed. Please try again."
        }

        def on_dialog_dismiss(instance):
            self.dialog_open = False

        self.dialog = MDDialog(
            text=error_messages.get(reason, error_messages["unknown"]),
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.bind(on_dismiss=on_dialog_dismiss)
        self.dialog_open = True
        self.dialog.open()
        
        
   

if __name__ == "__main__":
    freeze_support()  # This is necessary for multiprocessing in Windows

    # Load user cache (to check if the user is logged in)
    cache_data = load_user_cache()

    # Determine if we should auto-login (based on cache)
    should_auto_login = cache_data.get("logged_in", False) and cache_data.get("remember_me", True)

    if should_auto_login:
        # If auto-login is allowed, run the main app
        MsgApp().run()
    else:
        # If auto-login is not allowed and the user isn't logged in, clear credentials
        if cache_data.get("remember_me") is False:
            save_user_cache({
                "logged_in": False,
                "remember_me": False,
                "username": "",
                "password": ""
            })

        # Run the Notify app
        Notify().run()

    # After the main app has closed, check if the popup is needed
    cache_data = load_user_cache()  # Reload cache to check if popup is needed
    
    if cache_data.get("popup_needed", False):
        # Log that the popup is needed
        print("Popup needed, calling run_notify_popup()")
        
        # Make sure the cache data is correct and not None
        firstname = cache_data.get("firstname", "User")
        profile_thumb = cache_data.get("profile_thumb", "default.jpg")
        checkin_time = cache_data.get("checkin_time", "N/A")
        job_position = cache_data.get("job_position", "N/A")
        
        # Run the popup script
        run_notify_popup(firstname, profile_thumb, checkin_time, job_position)
    else:
        # If no popup is needed, log that and do nothing
        print("No popup needed")








