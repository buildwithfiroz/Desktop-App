from kivy.core.window import Window 
from kivy.animation import Animation
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from threading import Thread
from logic.logic import logic_main
import time


class CustomScreen(Screen):  
    def on_success_login(self):
        self.ids.login_button.text = ""  
        self.ids.login_button.disabled = True  
        # self.spinner = MDSpinner(
        #     size_hint=(None, None),
        #     size=(46, 46),
        #     pos_hint={"center_x": 0.5, "center_y": 0.5},
        #     active=True,
        #     palette=[
        #         [0.29, 0.84, 0.60, 1],
        #         [0.35, 0.32, 0.87, 1],
        #         [0.89, 0.36, 0.59, 1],
        #         [0.88, 0.91, 0.41, 1],
        #     ],
        # )
        # self.add_widget(self.spinner)
        #Clock.schedule_once(lambda dt: self.load_next_screen(), 2)

    def load_next_screen(self):
        self.remove_widget(self.children[-1])
        self.ids.login_button.text = "Login"
        self.ids.login_button.disabled = False


class Notify(MDApp):
    def build(self):
        self.login_start_time = None
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        Window.borderless = True
        Window.fullscreen = 'auto'

        self.sm = ScreenManager(transition=FadeTransition(duration=0.5))
        self.sm.add_widget(Builder.load_file("./Kv/splash.kv"))
        self.sm.add_widget(Builder.load_file("./Kv/login.kv"))

        return self.sm

    def on_start(self):
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
        Clock.schedule_once(lambda dt: setattr(self.sm, 'transition', NoTransition()), 0.6)

    def check_input_length(self):
        screen = self.sm.get_screen('Login')
        if screen:
            username = screen.ids.user.text
            password = screen.ids.pass_s.text
            screen.ids.login_button.disabled = len(username) < 3 or len(password) < 3

    def login_success_ui(self, data):
        end_time = time.perf_counter()
        total_time = end_time - self.login_start_time
        print(f"✅ Total time from login button click to showing result on UI: {total_time:.4f} seconds")

        # Optional: show login time in dialog
        self.dialog = MDDialog(
            text=f"✅ Login successful in {total_time:.2f} seconds",
            buttons=[MDFlatButton(text="OK", on_release=self.dismiss_dialog)]
        )
        self.dialog.open()

        print("Logged in user data:", data)



    def check_credentials(self):
        screen = self.sm.get_screen('Login')
        screen.ids.login_button.disabled = True
        username = screen.ids.user.text
        password = screen.ids.pass_s.text
        url = "https://demoerp.nexgeno.cloud/admin/timesheets_api/authenticate"

        def login_thread():
            self.login_start_time = time.perf_counter()  # Start timer
            result_data = logic_main(url, username, password)
            end_time = time.perf_counter()
            total_time = end_time - self.login_start_time

            if not result_data:
                print(f"❌ Total time from login button click to showing error dialog: {total_time:.4f} seconds")
                Clock.schedule_once(lambda dt: self.show_error_dialog("unauthorized"))
            else:
                print(f"✅ Total time from login button click to showing result on UI: {total_time:.4f} seconds")
                Clock.schedule_once(lambda dt: self.login_success_ui(result_data))

        Thread(target=login_thread).start()



    def show_error_dialog(self, reason="unknown"):
        if reason == "unauthorized":
            text = "Incorrect username or password. Please try again."
        elif reason == "dns":
            text = "Could not reach server. Check your internet connection."
        elif reason == "http_error":
            text = "Server error occurred. Try again later."
        else:
            text = "Login failed. Please try again."

        self.dialog = MDDialog(
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=self.dismiss_dialog)]
        )
        self.dialog.open()

    def dismiss_dialog(self, instance):
        self.dialog.dismiss()


if __name__ == '__main__':
    Notify().run()
