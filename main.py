"""
Aether Android — Modern AI Assistant
Kivy-based mobile version inspired by Mark-LVI and Brahma-Echo.
Features holographic-style UI, chat, Gemini AI, and Android speech recognition.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, BooleanProperty
import json
import threading
import time
from pathlib import Path

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from plyer import stt
    HAS_STT = True
except ImportError:
    HAS_STT = False

CONFIG_PATH = Path.home() / ".aether" / "config.json"
CONFIG_PATH.parent.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "assistant_name": "Aether"
}

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

class HoloCore(Widget):
    angle = NumericProperty(0)
    pulse = NumericProperty(0)
    listening = BooleanProperty(False)
    speaking = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.tick, 1/60)

    def tick(self, dt):
        self.angle = (self.angle + 1.5) % 360
        self.pulse = (self.pulse + 0.05) % 6.28
        self.canvas.clear()
        self.draw()

    def draw(self):
        with self.canvas:
            cx, cy = self.center_x, self.center_y
            r = min(self.width, self.height) / 2 - 10

            # Glow
            Color(0.05, 0.1, 0.2, 0.6)
            Ellipse(pos=(cx - r - 20, cy - r - 20), size=((r + 20)*2, (r + 20)*2))

            # Outer rings
            base_color = (0, 0.86, 1, 0.7) if not self.speaking else (0, 1, 0.7, 0.8)
            if self.listening:
                base_color = (0.4, 1, 0.6, 0.9)

            for i in range(3):
                Color(*base_color[:3], 0.7 - i * 0.15)
                offset = 8 * (0.5 + 0.5 * __import__("math").sin(self.pulse + i))
                Line(circle=(cx, cy, r - offset - i*8), width=2.5 - i*0.5)

            # Rotating arcs
            Color(0, 1, 1, 0.8)
            Line(circle=(cx, cy, r - 25), width=3, angle_start=self.angle, angle_end=self.angle + 100)
            Line(circle=(cx, cy, r - 25), width=2, angle_start=self.angle + 180, angle_end=self.angle + 250)

            # Center core
            core_r = 35 + 6 * __import__("math").sin(self.pulse)
            Color(0, 0.8, 1, 0.9)
            Ellipse(pos=(cx - core_r, cy - core_r), size=(core_r*2, core_r*2))

class AetherApp(App):
    def build(self):
        self.config = load_config()
        Window.clearcolor = get_color_from_hex("#0a0e17")

        root = BoxLayout(orientation="vertical", padding=16, spacing=12)

        # Header
        header = Label(
            text=f"✦ {self.config['assistant_name'].upper()}",
            size_hint_y=None, height=50,
            font_size=22, bold=True, color=get_color_from_hex("#38bdf8")
        )
        root.add_widget(header)

        # Holo core
        self.core = HoloCore(size_hint_y=None, height=220)
        root.add_widget(self.core)

        # Chat area
        self.chat_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.chat_layout)
        root.add_widget(scroll)

        # Input row
        input_row = BoxLayout(size_hint_y=None, height=50, spacing=8)
        self.input = TextInput(
            hint_text="Type a message...",
            multiline=False, size_hint_x=0.7,
            background_color=get_color_from_hex("#111827"),
            foreground_color=get_color_from_hex("#e0f2fe"),
            padding=[12, 12]
        )
        self.input.bind(on_text_validate=self.send_text)
        input_row.add_widget(self.input)

        mic_btn = Button(text="🎤", size_hint_x=0.15, background_color=get_color_from_hex("#0ea5e9"))
        mic_btn.bind(on_press=self.start_listen)
        input_row.add_widget(mic_btn)

        send_btn = Button(text="Send", size_hint_x=0.15, background_color=get_color_from_hex("#0ea5e9"))
        send_btn.bind(on_press=self.send_text)
        input_row.add_widget(send_btn)
        root.add_widget(input_row)

        # Settings button
        settings_btn = Button(
            text="⚙ Settings (API Key)", size_hint_y=None, height=44,
            background_color=get_color_from_hex("#1e3a5f")
        )
        settings_btn.bind(on_press=self.open_settings)
        root.add_widget(settings_btn)

        self.append_system(f"{self.config['assistant_name']} online. How can I help?")
        return root

    def append_message(self, text, color="#e0f2fe", bold=False):
        lbl = Label(
            text=text, size_hint_y=None, markup=True,
            text_size=(Window.width - 60, None),
            color=get_color_from_hex(color),
            halign="left", valign="top"
        )
        lbl.bind(texture_size=lbl.setter("size"))
        self.chat_layout.add_widget(lbl)

    def append_system(self, text):
        self.append_message(f"[color=#64748b]{text}[/color]")

    def append_user(self, text):
        self.append_message(f"[b]You:[/b] {text}")

    def append_ai(self, text):
        self.append_message(f"[b][color=#38bdf8]{self.config['assistant_name']}:[/color][/b] {text}", "#38bdf8")

    def send_text(self, *args):
        text = self.input.text.strip()
        if not text:
            return
        self.input.text = ""
        self.append_user(text)
        self.process_query(text)

    def start_listen(self, *args):
        if not HAS_STT:
            self.append_system("Speech recognition not available on this platform.")
            return
        self.core.listening = True
        self.append_system("Listening...")
        try:
            stt.start()
            Clock.schedule_once(self.check_speech, 1)
        except Exception as e:
            self.append_system(f"Mic error: {e}")
            self.core.listening = False

    def check_speech(self, dt):
        try:
            if stt.listening:
                Clock.schedule_once(self.check_speech, 0.5)
                return
            result = stt.results
            self.core.listening = False
            if result:
                text = result[0] if isinstance(result, list) else str(result)
                self.append_user(text)
                self.process_query(text)
            else:
                self.append_system("No speech detected.")
        except:
            self.core.listening = False

    def process_query(self, text):
        self.core.speaking = True
        threading.Thread(target=self._ai_worker, args=(text,), daemon=True).start()

    def _ai_worker(self, text):
        try:
            reply = self.get_ai_response(text)
        except Exception as e:
            reply = f"Sorry, I ran into an issue: {e}"
        Clock.schedule_once(lambda dt: self.deliver_reply(reply), 0)

    def get_ai_response(self, user_text):
        key = self.config.get("gemini_api_key", "").strip()
        if not key or not HAS_GEMINI:
            return "Please set a Gemini API key in Settings. Get a free key at aistudio.google.com"

        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        system = f"""You are {self.config['assistant_name']}, a helpful mobile AI assistant.
Keep responses concise and natural. You can answer questions, help with tasks, and provide information."""

        prompt = f"{system}\n\nUser: {user_text}"
        response = model.generate_content(prompt)
        return response.text.strip()

    def deliver_reply(self, text):
        self.core.speaking = False
        self.append_ai(text)

    def open_settings(self, *args):
        # Simple popup-style settings (in a real app use Popup or MDDialog)
        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput as TI

        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        key_input = TI(text=self.config.get("gemini_api_key", ""), password=True, hint_text="Gemini API Key")
        name_input = TI(text=self.config.get("assistant_name", "Aether"), hint_text="Assistant Name")
        content.add_widget(key_input)
        content.add_widget(name_input)

        def save(instance):
            self.config["gemini_api_key"] = key_input.text.strip()
            self.config["assistant_name"] = name_input.text.strip() or "Aether"
            save_config(self.config)
            popup.dismiss()
            self.append_system("Settings saved.")

        btn = Button(text="Save", size_hint_y=None, height=44)
        btn.bind(on_press=save)
        content.add_widget(btn)

        popup = Popup(title="Settings", content=content, size_hint=(0.9, 0.5))
        popup.open()

if __name__ == "__main__":
    AetherApp().run()
