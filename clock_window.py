#clock_window.py
from kivy.config import Config

# Must be set before importing any Kivy modules
Config.set('graphics', 'resizable', '0')    # Enable resizing
Config.set('graphics', 'borderless', '0')   # Show window border



from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.lang import Builder
import random
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
import json
import os
from datetime import datetime
import threading
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from dotenv import load_dotenv
import sys
from kivymd.uix.pickers import MDDatePicker
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.label import MDLabel
import datetime as dt
from kivy.metrics import dp
from kivymd.toast import toast
from kivy.app import App
from datetime import datetime, timedelta
import requests
import time
import socket
import logging
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime
from dotenv import load_dotenv
import os 

load_dotenv()

domain = os.getenv('ENDPOINT')



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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


def clock_in(session: requests.Session, username: str, password: str, url: str, timeout: float = 5.0):
    """
    Send a clock-in request to the server using stored username and password.
    """
    payload = {"email": username, "password": password}  # or whatever payload your clock-in API expects

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
        raise ValueError(f"Clock-in failed: {data.get('message', 'Unknown error')}")

    return data, elapsed, response.text







WEEKDAY_QUOTES = [
    "New goals, new opportunities—let’s crush it!",
    "Stay focused, the week is yours to conquer.",
    "Midweek hustle—halfway to greatness.",
    "Almost there, keep pushing forward.",
    "Finish strong, reflect on your wins.",
    "Kickstart the week with passion and purpose.",
    "Turn challenges into stepping stones.",
    "Progress isn’t perfection, it’s persistence.",
    "Keep moving, success is just around the corner.",
    "Celebrate small wins, they lead to big victories."
]

WEEKEND_QUOTES = [
    "Weekend loading… time to recharge those neurons.",
    "Fri-yay! Let the commits rest and the heart dance.",
    "Saturday smiles and zero stand-ups.",
    "Sunday reset—coffee, code, chill.",
    "Saturday: unplug to recharge for next week.",
    "Sunday: reflect, reset, and restart."
]
# ---------- LOGIN HISTORY UTILS ----------
CACHE_FILE = "user_cache.json"


class Attentions(Screen):
    _year  = dt.date.today().year
    _month = dt.date.today().month

    def on_pre_enter(self):
        self.refresh_calendar()          # current month on open

    def refresh_calendar(self):
        """Redraw grid for the current _year/_month."""
        data   = load_user_cache()
        logins = {entry.get("date") for entry in data.get("logins", []) if "date" in entry}


        # month label
        first = dt.date(self._year, self._month, 1)
        month_days = (first.replace(month=self._month % 12 + 1, day=1)
                      - dt.timedelta(days=1)).day
        present_in_month = sum(
            1 for d in range(1, month_days + 1)
            if dt.date(self._year, self._month, d).isoformat() in logins
        )
        self.ids.month_summary.text = (
            f"{first.strftime('%B %Y')} – {present_in_month} day(s) present"
        )

        # clear old widgets
        grid = self.ids.calendar_grid
        grid.clear_widgets()
        

        # weekday headers
        for wd in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            grid.add_widget(
                Label(
                    text=wd,
                    bold=True,
                    color=(.6, .6, .6, 1),
                    size_hint=(None, None),
                    size=(dp(40), dp(40)),
                    padding=(0, dp(12)) 
                )
            )


        # padding before 1st
        start_wd = first.weekday()  # 0 = Monday
        for _ in range(start_wd):
            grid.add_widget(Label())

        # day cells
        for d in range(1, month_days + 1):
            iso = dt.date(self._year, self._month, d).isoformat()
            mark = iso in logins
            bg = (0.2, 0.7, 0.3, 0.9) if mark else (0.1, 0.1, 0.1, 0.7)

            day_lbl = Label(
                text=str(d),
                color=(1,1,1,1) if mark else (.8,.8,.8,1),
                bold=mark,
                size_hint_y=None,
                height=dp(36),          # uniform height
                padding=(dp(6), dp(6))  # internal padding
            )
            with day_lbl.canvas.before:
                Color(*bg)
                Rectangle(pos=day_lbl.pos, size=day_lbl.size)
            day_lbl.bind(size=lambda w, _: setattr(w.canvas.before.children[-1], 'size', w.size),
                        pos=lambda w, _: setattr(w.canvas.before.children[-1], 'pos', w.pos))
            self.ids.calendar_grid.add_widget(day_lbl)
            
        
        
        
load_dotenv()


clock_in_url = os.getenv('URL')
reset_hour = int(os.getenv("RESET_HOUR", 8))      # fallback to 8
reset_minute = int(os.getenv("RESET_MINUTE", 59)) # fallback to 59






def save_user_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
        
def prune_old_logins(logins, keep_days=30):
    cutoff = (dt.datetime.utcnow() - dt.timedelta(days=keep_days)).date().isoformat()
    return [entry for entry in logins if entry.get("date", "") >= cutoff]


def days_since_last_login(logins):
    if not logins:
        return None
    dates = [entry.get("date") for entry in logins if "date" in entry]
    if not dates:
        return None
    last = dt.datetime.fromisoformat(max(dates)).date()
    return (dt.date.today() - last).days


def update_env_var(key, value, env_path=".env"):
    from dotenv import dotenv_values

    # Read current env
    current_env = dotenv_values(env_path)

    # Overwrite or add the key
    current_env[key] = value

    # Write back
    with open(env_path, "w") as f:
        for k, v in current_env.items():
            f.write(f"{k}={v}\n")


def load_user_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

user_cache = load_user_cache()


def perform_clock_in_request():
    username = user_cache.get("username")
    password = user_cache.get("password")

    if not username or not password:
        print("No saved credentials found. Please login again.")
        return

    app_ref = App.get_running_app()


    def clock_in_task(app):
        
        user_cache["clocked_in"] = True
        user_cache["clock_in_time"] = datetime.now().isoformat()
        save_user_cache(user_cache)

        
        
        
        try:
            session = create_session()
            data, duration, _ = clock_in(session, username, password, clock_in_url)

            if not data:
                raise ValueError("Empty or invalid response from server")

            # --- SUCCESS PATH ---
            print(f"✅ Clock-in succeeded in {duration:.2f}s: {data}")

            # ✅ Update log and status *after* success
            update_clock_in_status(user_cache)
            update_login_log(user_cache)
            
            
            if hasattr(app, 'clock_label_event') and app.clock_label_event:
                app.clock_label_event.cancel()
                app.clock_label_event = None

            # Reset and start timer
            app.timer_seconds = 0
            app.timer_event = Clock.schedule_interval(app.update_timer, 1)

            # Set clocked-in state
            app.clocked_in = True


        except Exception as e:
            # --- FAILURE PATH ---
            Clock.schedule_once(lambda _: toast("Server error!"))
            print(f"❌ Clock-in failed: {e}")

            # show error label
            Clock.schedule_once(lambda _: toast("Server Error"))


            # re-enable the clock-in button immediately
            Clock.schedule_once(
                lambda _: setattr(
                    app.root.get_screen('clock').ids.check_in_button, 'disabled', False
                )
            )
            Clock.schedule_once(
                lambda _: setattr(
                    app.root.get_screen('clock').ids.check_in_button,
                    'md_bg_color',
                    (0.145, 0.827, 0.4, 0.72)
                )
            )

    threading.Thread(target=lambda: clock_in_task(app_ref), daemon=True).start()


def update_clock_in_status(user_cache, clocked_in=True):
    user_cache.update({
        "clocked_in": clocked_in,
        "clock_in_time": datetime.now().isoformat()
    })
    save_user_cache(user_cache)

def update_login_log(user_cache):
    today_str = datetime.now().strftime("%Y-%m-%d")
    logins = user_cache.get("logins", [])
    
    for entry in logins:
        if entry.get("date") == today_str:
            entry["count"] += 1
            break
    else:
        logins.append({"date": today_str, "count": 1})

    user_cache["logins"] = logins

    # Ensure keys exist
    if "clocked_in" not in user_cache:
        user_cache["clocked_in"] = False
    if "clock_in_time" not in user_cache:
        user_cache["clock_in_time"] = ""

    save_user_cache(user_cache)

KV = """
ScreenManager:
    ClockScreen:
    GeneralScreen:
    SoftwareUpdateScreen:
    Attentions:


    
<ClockScreen>:
    name: 'clock'
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
                    id: motivation_label
                    text: ""
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
                            on_release:
                                app.start_action()
                                app.on_clock_in_button_press()
                                


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
                            
                                        
     

<GeneralScreen>:
    name: 'general'
    MDFloatLayout:

        MDCard:
            size_hint: 0.9, 0.25
            pos_hint: {"center_x": 0.5, "top": 0.95}
            radius: [20, 20, 20, 20]
            md_bg_color: 0.15, 0.15, 0.15, 1
            elevation: 4
            BoxLayout:
                orientation: 'vertical'
                spacing: "10dp"
                padding: "10dp"
                # ── circular profile picture
                FitImage:
                    id: profile_image
                    source: "./tmp/ai_nexgeno_in_thumb.jpg"
                    size_hint: None, None
                    size: dp(72), dp(72)
                    pos_hint: {"center_x": 0.5}
                    radius: [dp(36)]  # ½ of size → perfect circle
                    allow_stretch: True
                    keep_ratio: True
                MDLabel:
                    text: "General"
                    font_style: "H6"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                MDLabel:
                    text: "Manage your overall setup and API for Login App."
                    halign: "center"
                    font_style: "Caption"
                    theme_text_color: "Custom"
                    text_color: 0.8, 0.8, 0.8, 1

        MDList:
            pos_hint: {"center_y": 0.53}
            spacing: "10dp"


            OneLineIconListItem:
                text: "Key"
                on_release: app.show_password_dialog()
                IconLeftWidget:
                    icon: "api"
                    
            OneLineIconListItem:
                text: "Attendance"
                on_release: app.attentions()
                IconLeftWidget:
                    icon: "calendar"

            OneLineIconListItem:
                text: "Logout"
                on_release: app.show_logout_confirmation()
                IconLeftWidget:
                    icon: "logout"



<SoftwareUpdateScreen>:
    name: 'software_update'
    MDScreen:

        MDTopAppBar:
            title: "Key"
            elevation: 4
            pos_hint: {"top": 1}
            left_action_items: [['arrow-left', lambda x: app.go_back()]]

            

        MDBoxLayout:
            orientation: "vertical"
            spacing: "20dp"
            padding: "20dp"
            pos_hint: {"top": 0.75}
            size_hint_y: None
            height: self.minimum_height

            MDTextField:
                id: domain_field
                hint_text: "Domain"
                mode: "rectangle"
                icon_right: "web"
                size_hint_x: 1

            MDTextField:
                id: url_field
                hint_text: "URL"
                mode: "rectangle"
                icon_right: "link"
                size_hint_x: 1
                    
                    
            MDRaisedButton:
                id: login_button
                text: "Update"
                on_release: app.submit_software_update(domain_field.text, url_field.text)
                size_hint: 1, None
                
<Attentions>:
    name: "Cal"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Attendance Calendar"
            elevation: 4
            left_action_items: [['arrow-left', app.go_back]]

        MDLabel:
            id: month_summary
            halign: "center"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
            padding: [0, dp(80), 0, 0] 

        # ── center the grid horizontally and vertically ──
        AnchorLayout:
            size_hint_y: 1
            anchor_x: 'center'
            anchor_y: 'center'
            padding: [0, 0, 0, dp(60)]   # push everything up by 30 dp

            GridLayout:
                id: calendar_grid
                cols: 7
                spacing: dp(1)
                padding: dp(1)
                size_hint: None, None
                width:  dp(40*7 + 30)   # 7 cells + spacing/padding
                height: self.minimum_height
"""

class ClockScreen(Screen):
    pass

class GeneralScreen(Screen):
    pass

class SoftwareUpdateScreen(Screen):
    pass

class MsgApp(MDApp):
    password_dialog = None
    error_dialog = None
    logout_dialog = None


    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_seconds = 0
        self.timer_event = None
        self.clock_event = None
        self.clocked_in = False
        self.endpoint = os.getenv('ENDPOINT', '')
        self.url = os.getenv('URL', '')
        self.admin_pass = os.getenv('ADMIN_PASS', '123')
        
        
    def show_date_picker(self):
        picker = MDDatePicker(mode="picker", max_date=dt.date.today())
        picker.bind(on_save=self.on_date_selected)
        picker.open()

    def on_date_selected(self, instance, value, *args):
        iso_date = value.isoformat()
        data = load_user_cache()
        logins = set(data.setdefault("logins", []))
        logins.add(iso_date)
        data["logins"] = sorted(logins)
        save_user_cache(data)

        # refresh the calendar if it’s open
        att = self.root.get_screen("Cal")
        if att.manager.current == "Cal":
            att.refresh_calendar()

    def build(self):
        self.title = 'MCRM'
        Window.size = (350, 580)
        Window.minimum_size = Window.size
        Window.top = 50
        Window.left = 890
        Window.title = "MCRM"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        Window.clearcolor = (0, 0, 0, 0)
        Config.set('graphics', 'resizable', False)
        return Builder.load_string(KV)
    
    def attentions(self):
        self.root.current = "Cal"
        
    def go_back(self, instance=None):
        self.root.current = "general"
        
    def pick_month(self):
    # simply forward to the calendar screen
        self.root.get_screen('Cal').pick_month()
    
    def show_success_dialog(self, message):
        success_dialog = MDDialog(
            text=message,
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: success_dialog.dismiss())
            ]
        )
        success_dialog.open()

    def on_start(self):
        try:
            if os.path.exists("user_cache.json"):
                with open("user_cache.json", "r") as file:
                    user_data = json.load(file)

                firstname = user_data.get("firstname", "User").title()
                clock_screen = self.root.get_screen("clock")
                clock_screen.ids.user_name.text = firstname
                clock_screen.ids.profile_image.source = user_data.get("profile_thumb", "Wel.png")

            clocked_in = user_cache.get("clocked_in", False)
            clock_in_time_str = user_cache.get("clock_in_time")

            if clocked_in and clock_in_time_str:
                clock_in_time = datetime.fromisoformat(clock_in_time_str)
                now = datetime.now()

                # Reset at 8:59 AM the next day
                reset_time = (clock_in_time + timedelta(days=1)).replace(
                    hour=reset_hour,
                    minute=reset_minute,
                    second=0,
                    microsecond=0
                )

                if now < reset_time:
                    # Still within clock-in window
                    self.clocked_in = True
                    self.timer_seconds = int((now - clock_in_time).total_seconds())
                    self.timer_event = Clock.schedule_interval(self.update_timer, 1)

                    # Disable button
                    btn = self.root.get_screen("clock").ids.check_in_button
                    btn.disabled = True
                    btn.md_bg_color = (0.4, 0.4, 0.4, 0.6)
                    toast("Already clocked in")
                else:
                    # Reset for new day
                    user_cache["clocked_in"] = False
                    user_cache["clock_in_time"] = None
                    save_user_cache(user_cache)

        except Exception as e:
            print("Error during startup:", e)

        # Continue with the rest of on_start...
        self.clock_label_event = Clock.schedule_interval(self.update_clock_label, 1)

        # 1. Record today’s login
        logins = user_cache.setdefault("logins", [])
        logins = prune_old_logins(logins)
        user_cache["logins"] = logins

        # 2. Pick quote based on last login and day of the week
        days = days_since_last_login(logins)

        if days is None:
            quote = "First time? Let’s make it legendary!"
        elif days == 0:
            quote = "Back again—your flow is unstoppable!"
        elif days == 1:
            quote = "All good—didn’t see you yesterday. Ready?"
        elif 2 <= days <= 3:
            quote = "Missed you! Let’s pick up the pace."
        else:
            quote = "Long time no see—welcome back to the grind!"

        # Weekday vs weekend override logic
        weekday = datetime.today().weekday()  # 0..6
        if weekday >= 4:  # Friday after 12 pm -> weekend vibe
            if weekday == 4 and datetime.now().hour < 12:
                pass  # keep weekday quote until noon
            else:
                quote = random.choice(WEEKEND_QUOTES)  # Random weekend quote
        else:
            quote = random.choice(WEEKDAY_QUOTES)  # Random weekday quote

        # Add motivational boost based on login days
        if days is not None:
            if days <= 3:
                motivational_boost = "You're on fire—keep it up!"
            elif days <= 7:
                motivational_boost = "Consistency is key. Keep pushing!"
            else:
                motivational_boost = "Great progress! You're building momentum."

            quote += f" {motivational_boost}"

        # 3. Push to label
        clock_screen = self.root.get_screen("clock")
        clock_screen.ids.motivation_label.text = quote

        # Bind keyboard
        Window.bind(on_key_down=self.on_key_down)

        # Pre-fill Software Update fields
        domain_field = self.root.get_screen("software_update").ids.domain_field
        url_field = self.root.get_screen("software_update").ids.url_field
        domain_field.text = self.endpoint
        url_field.text = self.url


    def update_clock_label(self, dt):
        current_time = datetime.now().strftime("%I:%M %p")  # 12-hour format
        self.root.get_screen('clock').ids.timer_label.text = current_time


    def update_timer(self, dt):
        self.timer_seconds += 1
        hours, remainder = divmod(self.timer_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.root.get_screen('clock').ids.timer_label.text = time_str


    def start_action(self):
        """
        Only toggle the UI state here.
        The actual timer is started only AFTER the server confirms the clock-in.
        """
        clock_screen = self.root.get_screen("clock")
        btn = clock_screen.ids.check_in_button

        if not self.clocked_in:
            # disable button so user cannot click again while request is running
            btn.disabled = True
            btn.md_bg_color = (0.7, 0.7, 0.7, 0.9)
            print("⏳ Clock-in request sent …")
        else:
            # clock-out path – safe to stop the timer immediately
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None

            btn.disabled = False
            btn.md_bg_color = (0.145, 0.827, 0.4, 0.72)
            self.clocked_in = False
            print("🛑 Clocked out. Timer stopped.")

    
    
    
    
    def on_clock_in_button_press(self):
        perform_clock_in_request()





    
    
    
    def show_password_dialog(self):
        if not self.password_dialog:
            self.password_text_field = MDTextField(
                hint_text="Enter password",
                password=True,
                size_hint_x=None,
                width=200,
            )
            self.password_dialog = MDDialog(
                title="Enter password",
                type="custom",
                content_cls=self.password_text_field,
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=self.dismiss_password_dialog
                    ),
                    MDFlatButton(
                        text="OK", on_release=self.verify_password_dialog
                    ),
                ],
            )
        self.password_dialog.open()

    def dismiss_password_dialog(self, *args):
        self.password_text_field.text = ""  # Clear input
        self.password_dialog.dismiss()


    def verify_password_dialog(self, *args):
        entered_pass = self.password_text_field.text
        self.password_text_field.text = ""  # Clear input

        if entered_pass == self.admin_pass:
            self.password_dialog.dismiss()
            self.show_software_update_screen()
        else:
            self.password_dialog.dismiss()
            self.show_error_dialog("Incorrect password!")


    def show_error_dialog(self, message):
        if not self.error_dialog:
            self.error_dialog = MDDialog(
                title="Error",
                text=message,
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.error_dialog.dismiss())],
            )
        else:
            self.error_dialog.text = message
        self.error_dialog.open()

    def show_software_update_screen(self):
        self.root.current = "software_update"

    def submit_software_update(self, domain, url):
        
        domain = domain.strip()
        url = url.strip()
        
        if not domain or not url:
            self.show_error_dialog("Domain and URL cannot be empty.")
            return
        
        
        # Save or apply update logic here
        print(f"Updating Domain: {domain}, URL: {url}")
        self.endpoint = domain
        self.url = url

        self.root.current = "general"
        
        update_env_var("ENDPOINT", domain)
        update_env_var("URL", url)

        self.endpoint = domain
        self.url = url
        
        self.show_success_dialog("Update successful!")

    def show_logout_confirmation(self):
        if not self.logout_dialog:
            self.logout_dialog = MDDialog(
                title="Confirm Logout",
                text="Are you sure you want to logout?",
                buttons=[
                    MDFlatButton(text="Cancel", on_release=lambda x: self.logout_dialog.dismiss()),
                    MDFlatButton(text="Logout", on_release=self.logout),
                ],
            )
        self.logout_dialog.open()

    def logout(self, *args):
        
        try:
            with open("user_cache.json", "r") as f:
                cache_data = json.load(f)

            cache_data["remember_me"] = False

            with open("user_cache.json", "w") as f:
                json.dump(cache_data, f, indent=4)

        except Exception as e:
            self.show_error_dialog("unknown")
            print(f"Error updating user_cache.json on logout: {e}")
            return
        
        
        print("User logged out.")
        
        
        self.logout_dialog.dismiss()
        self.root.current = "clock"
        self.stop()



    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        # Handle key name for tuples or string
        key_name = None
        if isinstance(key, tuple):
            # If key is tuple like (code, name)
            key_name = key[1]
        elif codepoint:
            key_name = codepoint.lower()

        mod = set(m.lower() for m in modifiers)

        # Spacebar toggles clock in/out
        if codepoint == " ":
            self.start_action()
            return True

        if key == 27: 
            if self.password_dialog and self.password_dialog.open:
                self.password_dialog.dismiss()
                return True
            if self.error_dialog and self.error_dialog.open:
                self.error_dialog.dismiss()
                return True
            if self.logout_dialog and self.logout_dialog.open:
                self.logout_dialog.dismiss()
                return True
            return False

        # Ctrl + key combos
        if 'ctrl' in mod and key_name:
            if key_name == 's':
                print("Ctrl+S detected → Show Settings Screen")
                self.root.current = 'general'
                return True
            
            
            elif key_name == 'b':
                self.root.current = 'clock'
                return True
                
            elif key_name == 'l':
                print("Ctrl+L detected → Logout")
                # Trigger logout logic here, e.g., open logout dialog
                if self.logout_dialog:
                    self.logout_dialog.open()
                return True

        return False

