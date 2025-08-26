from kivy.config import Config

# Must be set before importing any Kivy modules
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'borderless', '0')

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
from notify_popup import NotifyPopupApp  # Popup app
from logic.logic import logic_main
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

load_dotenv()

url = os.getenv('URL')




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


def run_notify_popup(firstname, profile_thumb, checkin_time, job_position):
    python_executable = sys.executable
    script_path = os.path.abspath("notify_popup.py")
    args = [
        python_executable,
        script_path,
        firstname,
        profile_thumb,
        checkin_time,
        job_position
    ]
    args = ["python", "notify_popup.py"]
    args += [str(arg) if arg is not None else "null" for arg in [firstname, profile_thumb, checkin_time, job_position]]
    subprocess.Popen(args)


    
    


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
        
        self.error_sound = SoundLoader.load('./src/audio/delete.mp3') or None

        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))
        self.sm.add_widget(Builder.load_file("./Kv/splash.kv"))
        self.sm.add_widget(Builder.load_file("./Kv/login.kv"))
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
        profile_thumb_url = data.get("profile_thumb", "src/img/logo.png")
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

            # Launch popup
            run_notify_popup(firstname, img_path, checkin_time, job_position)

            # Exit current app
            self.stop()

        def background_image_worker():
            print(f"[🔁 Downloading profile image from: {profile_thumb_url}]")
            if download_and_optimize_image(profile_thumb_url, local_img_path):
                print("[✅ Image Downloaded]")
                img_path = local_img_path
            else:
                print("[⚠️ Falling back to default image]")
                img_path = "src/img/logo.png"
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
    freeze_support()
    cache_data = load_user_cache()

    # Only auto-login if both logged_in and remember_me are True
    should_auto_login = cache_data.get("logged_in", False) and cache_data.get("remember_me", True)
    
    if should_auto_login:
        MsgApp().run()
    else:
        # Clear credentials if remember_me was unchecked
        if cache_data.get("remember_me") is False:
            save_user_cache({
                "logged_in": False,
                "remember_me": False,
                "username": "",
                "password": ""
            })
        Notify().run()
