from kivy.config import Config


Config.set('graphics', 'resizable', '0')    # Enable resizing
Config.set('graphics', 'borderless', '1')   # Show window border

from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import sys

KV = """
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

        self.success_sound = SoundLoader.load('./src/audio/ting.mp3') or None
        if self.success_sound:
            self.success_sound.play()

        screen = Builder.load_string(KV)
        
        
        display_name = self.firstname
        if len(display_name) >= 12:
            display_name = display_name[:9] + ".."  

        screen.ids.user_name.text = display_name    


        screen.ids.user_pic.source = self.profile_thumb
        screen.ids.time_label.text = self.checkin_time
        screen.ids.user_position.text = self.job_position

        # Close the app after 7 seconds of inactivity
        Clock.schedule_once(self.close_application, 5)
        
        return screen
    
    def close_application(self, dt=None):
        """Close the application."""
        self.stop()


if __name__ == "__main__":
    firstname = sys.argv[1] if len(sys.argv) > 1 else "Firoz Shaikh"
    profile_thumb = sys.argv[2] if len(sys.argv) > 2 else "src/img/logo.png"
    checkin_time = sys.argv[3] if len(sys.argv) > 3 else "09:00 AM"
    job_position = sys.argv[4] if len(sys.argv) > 4 else "HOD - AI"

    NotifyPopupApp(firstname, profile_thumb, checkin_time, job_position).run()
