from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from datetime import datetime
from kivy.clock import Clock ,ctypes
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader


# Windows API Constants for adding shadow
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_NOACTIVATE = 0x08000000
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

KV = '''

<MyWidget>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 0.8, 0.8  # Background color with transparency (0.8 alpha)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [30]  # Adjust corner radius here

        
BoxLayout:
    orientation: 'vertical'

    MDFloatLayout:
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        MDIconButton:
            icon: "close-circle"
            theme_text_color: "Custom"
            icon_size: "20sp"
            text_color: 1, 0, 0, 1
            pos_hint: {'center_x': 0.09, 'center_y': 0.93}
            opacity: 0.9
            on_release: app.close_application()
        
        MDIconButton:
            icon: "minus-circle"
            theme_text_color: "Custom"
            icon_size: "20sp"
            pos_hint: {'center_x': 0.92, 'center_y': 0.93}
            opacity: 0.9
            on_release: app.minimize_window()
            
        MDFloatLayout:
            pos_hint: {'center_x': 0.5, 'center_y': 0.57}

            MDLabel:
                text: "[b] As[color=#673AB7]salam [/color]Walekum! [/b]"
                theme_text_color: 'Custom'
                markup: True
                halign: 'center'  # Center the text horizontally
                opacity: 0.8
                text_color: 0.5, 0.5, 0.5, 1
                font_style: 'H6'
                pos_hint: {'center_x': 0.51 ,  'center_y': 0.82}

            MDLabel:
                id: user_name
                text: 'Wans'
                halign: 'center'  
                valign: 'center' 
                size: self.texture_size  
                pos_hint: {'center_x': 0.5, 'center_y': 0.75}  
                theme_text_color: 'Custom'
                text_color: 0.5, 0.5, 0.5, 1
                font_style: 'Body2'
            
         # Circular background
        FloatLayout:
            size_hint: (None, None)
            size: (320, 320)  
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
            
            canvas:
                Color:
                    rgba: 0.5, 0.5, 0.8, 1  
                Ellipse:
                    pos: self.pos
                    size: self.size

            # Image widget inside the circular background
            Image:
                source: "Wel.png"  
                size_hint: (1.4, 1.4)  
                pos_hint: {'center_x': 0.5, 'center_y': 0.5} 
                allow_stretch: True 
                
        FloatLayout:
            size_hint: (None, None)
            size: (320, 320)  
            pos_hint: {'center_x':0.5, 'center_y': 0.55} 

            MDIconButton:
                id: check_in_button
                icon: "check-circle"
                icon_size: "78sp"
                theme_text_color: "Custom"  # Make sure this is set to Custom to apply your custom color
                text_color: 0.149, 0.831, 0.29, 1
                on_release: app.start_action()  
                pos_hint: {'center_x': -0.01, 'center_y': -0.36}
                
            MDLabel:
                id: clock_in_label
                text: 'Clock-In'
                pos_hint: {'center_x': 0.3, 'center_y': -0.7}
                theme_text_color: 'Custom'
                text_color: 1,1,1,1
                font_style: 'Body2'

            MDIconButton:
                id: check_out_button  # Add an ID for the check-out button
                icon: "location-exit"
                icon_size: "68sp"
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1  # Classic red (RGBA)
                on_release: app.stop_action() 
                pos_hint: {'center_x': 1, 'center_y': -0.36}
                disabled: True  # Initially disabled
                
            MDLabel:
                id:  clock_out_label
                text: 'Clock-Out'
                pos_hint: {'center_x': 1.3, 'center_y': -0.7}
                theme_text_color: 'Custom'
                text_color: 1,1,1,0.3
                font_style: 'Body2'
                
        MDLabel:
            id: timer_label
            text: "Check-in To Start"
            halign: 'center'  # Center the text horizontally
            width: self.texture_size[0]  # Set width to the width of the text
            pos_hint: {'center_x': 0.5, 'center_y': 0.95}  # Center the label
            markup: True
            theme_text_color: 'Custom'
            text_color: 0.5, 0.5, 0.5, 0.5
            font_name: "Nova"
            font_style: 'Body2'
            
         # MDLabel:
        #     text: " Logged-In : "
        #     pos_hint: {'center_x': 0.59, 'center_y': 0.2}
        #     markup: True
        #     theme_text_color: 'Custom'
        #     text_color: 0.5, 0.5, 0.5, 0.5
        #     font_name: "Nova"
        #     font_style: 'Body2'

                    
        # MDLabel:
        #     id: time_label
        #     text: ""
        #     pos_hint: {'center_x': 0.76, 'center_y': 0.2}
        #     theme_text_color: 'Custom'
        #     text_color:  1, 1, 1, 0.3
        #     font_style: 'Body2'
'''


class MyWidget(BoxLayout):
    pass

class MsgApp(MDApp):
    
    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.timer_seconds = 0  # Start timer at 0
            self.timer_event = None  # To keep track of the timer event
            
    
            
            
    def start_action(self):
        self.timer_seconds += 1  # Increment timer by 1 second
        self.update_timer_label()  # Update the label immediately

        if self.timer_event is None:  # Prevent multiple timers from starting
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)  # Update every second

        # Set opacity for the check-in button
        self.root.ids.check_in_button.opacity = 0.3  # Reduce opacity
        self.root.ids.check_out_button.opacity = 1.0  # Max opacity for the check-out button
        
        # Change text opacity for 'Clock-In' and 'Clock-Out' labels
        self.root.ids.clock_in_label.color = (1, 1, 1, 0.3)  # Reduce opacity for 'Clock-In' label
        self.root.ids.clock_out_label.color = (1, 1, 1, 1)   # Max opacity for 'Clock-Out' label
        
        self.root.ids.timer_label.color = [1,1,1,0.74]

        # Disable check-in button and enable check-out button
        self.root.ids.check_in_button.disabled = True
        self.root.ids.check_out_button.disabled = False

    def update_timer(self, dt):
        self.timer_seconds += 1  # Increment the timer by 1 second
        self.update_timer_label()

    def update_timer_label(self):
        Hours = self.timer_seconds // 3600
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.root.ids.timer_label.text = f"{Hours:02}:{minutes:02d}:{seconds:02d}"  # Format as MM:SS

    def stop_action(self):
        self.timer_seconds = 0  # Reset timer to 0
        if self.timer_event:  # Stop the timer if it's running
            self.timer_event.cancel()
            self.timer_event = None

        self.update_timer_label()  # Update the label to reflect the reset

        # Reset opacities when check-out button is pressed
        self.root.ids.check_in_button.opacity = 1.0  # Reset opacity to max
        self.root.ids.check_out_button.opacity = 0.3  # Reduce opacity
        
        # Change text opacity for 'Clock-In' and 'Clock-Out' labels
        self.root.ids.clock_in_label.color = (1, 1, 1, 1)   # Max opacity for 'Clock-In' label
        self.root.ids.clock_out_label.color = (1, 1, 1, 0.3)  # Reduce opacity for 'Clock-Out' label

        # Disable check-out button and enable check-in button
        self.root.ids.check_out_button.disabled = True
        self.root.ids.check_in_button.disabled = False
        
    def set_shadow(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()  # Get the window handle
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        # Add shadow style
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_APPWINDOW)
        
    def close_application(self):
        self.stop()
        
    def minimize_window(self):
        Window.minimize() 

    def build(self):
        sound = SoundLoader.load('ting.mp3')
        if sound:
            sound.play()
        Window.size = [285, 420]
        Window.minimum_size = Window.size
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        screen = Builder.load_string(KV)
        
        current_datetime1 = datetime.now().strftime("%I:%M:%S %p")
        # screen.ids.time_label.text = f"{current_datetime1}"
        screen_width, screen_height = Window.size
        window_width, window_height = 815, 1250
        Window.left = screen_width - window_width
        Window.top = screen_height - window_height
        
        # Set transparency of the window background
        Window.clearcolor = (0, 0, 0, 0)  # Fully transparent background color

        # Set opacity of the window (affects the entire window)
        Window.opacity = 0.935  # 90% opacity

        Window.borderless = True
        
        return screen

if __name__ == '__main__':
    MsgApp().run()
