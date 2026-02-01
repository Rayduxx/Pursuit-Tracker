import tkinter as tk
import time
import keyboard
import mouse
import threading
import winsound
import json
import os
from collections import deque

CONFIG_FILE = "timer_config.json"

class RacingTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Racing Timer")
        self.root.geometry("250x200+10+10")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.8)
        self.bg_color = "#1e1e1e"
        self.text_color = "#00ff00"
        self.secondary_color = "#ffffff"
        self.root.configure(bg=self.bg_color)
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = deque(maxlen=5)
        self.bind_config = {"type": "keyboard", "value": "x"}
        self.ui_config = {
            "opacity": 0.8, 
            "size": "250x200",
            "text_color": "#00ff00"
        }
        self.load_config()
        self.bg_color = "#1e1e1e"
        self.text_color = self.ui_config.get("text_color", "#00ff00")
        self.secondary_color = "#ffffff"
        
        self.root.wm_attributes("-alpha", self.ui_config.get("opacity", 0.8))
        self.root.geometry(self.ui_config.get("size", "250x200") + "+10+10")
        self.root.configure(bg=self.bg_color)
        
        self.preset_duration = None 
        self.presets = {
            "Tier 1": {
                "Time Assessment": 105.0
            },
            "Tier 2": {
                "Time Assessment": 103.0,
                "Jump Assessment": 145.0,
                "Precision Assessment": 58.0
            },
            "Tier 3": {
                "Time Assessment": 169.0,
                "Jump Assessment": 105.0,
                "Precision Assessment": 96.0
            }
        }

        self.setup_ui()
        
        self.hook_active = False
        self.start_listening()
        
        self.update_timer()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.bind_config = data.get('bind', self.bind_config)
                    self.ui_config = data.get('ui', self.ui_config)
            except:
                pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    'bind': self.bind_config,
                    'ui': self.ui_config
                }, f)
        except:
            pass

    def setup_ui(self):
        self.time_label = tk.Label(self.root, text="00:00.000", font=("Consolas", 24, "bold"), bg=self.bg_color, fg=self.text_color)
        self.time_label.pack(pady=(10, 5), fill='x')
        
        self.header_label = tk.Label(self.root, text="Last 5 Runs:", font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.secondary_color, anchor="w")
        self.header_label.pack(fill='x', padx=10)
        
        self.laps_frame = tk.Frame(self.root, bg=self.bg_color)
        self.laps_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.lap_labels = []
        for _ in range(5):
            lbl = tk.Label(self.laps_frame, text="--:--.---", font=("Consolas", 10), bg=self.bg_color, fg=self.secondary_color, anchor="w")
            lbl.pack(fill='x')
            self.lap_labels.append(lbl)
            
        self.instr = tk.Label(self.root, text=self.get_bind_text(), font=("Arial", 8), bg=self.bg_color, fg="#888888")
        self.instr.pack(side="bottom", pady=5)

        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.do_move)
        
        self.menu = tk.Menu(self.root, tearoff=0)
        
        self.presets_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Presets (Countdown)", menu=self.presets_menu)
        self.presets_menu.add_command(label="None (Count Up)", command=self.disable_preset)
        self.presets_menu.add_separator()
        
        self.add_presets_to_menu(self.presets_menu, self.presets)

        self.ui_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Customize UI", menu=self.ui_menu)
        
        self.opacity_menu = tk.Menu(self.ui_menu, tearoff=0)
        self.ui_menu.add_cascade(label="Opacity", menu=self.opacity_menu)
        for val, label in [(0.4, "40%"), (0.6, "60%"), (0.8, "80%"), (1.0, "100%")]:
            self.opacity_menu.add_command(label=label, command=lambda v=val: self.set_opacity(v))
            
        self.scale_menu = tk.Menu(self.ui_menu, tearoff=0)
        self.ui_menu.add_cascade(label="Window Size", menu=self.scale_menu)
        self.scale_menu.add_command(label="Small (200x150)", command=lambda: self.set_window_size("200x150"))
        self.scale_menu.add_command(label="Standard (250x200)", command=lambda: self.set_window_size("250x200"))
        self.scale_menu.add_command(label="Large (300x250)", command=lambda: self.set_window_size("300x250"))
        
        self.ui_menu.add_command(label="Change Text Color", command=self.ask_color)

        self.menu.add_separator()
        self.menu.add_command(label="Change Hotkey", command=self.change_bind_mode)
        self.menu.add_command(label="Reset Laps", command=self.reset_laps)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.close_app)
        self.root.bind("<Button-3>", self.show_menu)

    def add_presets_to_menu(self, parent_menu, presets):
        for name, data in presets.items():
            if isinstance(data, dict):
                sub_menu = tk.Menu(parent_menu, tearoff=0)
                parent_menu.add_cascade(label=name, menu=sub_menu)
                self.add_presets_to_menu(sub_menu, data)
            else:
                parent_menu.add_command(
                    label=f"{name} ({self.format_time(data, force_positive=True)})", 
                    command=lambda d=data: self.enable_preset(d)
                )
        
    def get_bind_text(self):
        t = self.bind_config['type']
        v = self.bind_config['value']
        return f"Bind: {v.upper()} ({t})"

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def enable_preset(self, duration):
        self.preset_duration = duration
        if not self.running:
            self.time_label.config(text=self.format_time(duration))
            
    def disable_preset(self):
        self.preset_duration = None
        if not self.running:
            self.time_label.config(text="00:00.000")

    def reset_laps(self):
        self.lap_times.clear()
        self.update_laps_display()

    def close_app(self):
        self.stop_listening()
        self.root.destroy()
        os._exit(0)

    def toggle_timer(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            self.beep(start=True)
            self.time_label.config(fg="#00ff00")
        else:
            final_time = time.time() - self.start_time
            self.running = False
            self.beep(start=False)
            self.time_label.config(fg="#ff5555")
            self.lap_times.appendleft(self.format_time(final_time))
            self.update_laps_display()
            
            if self.preset_duration is not None:
                remaining = self.preset_duration - final_time
                self.time_label.config(text=self.format_time(remaining))

    def update_laps_display(self):
        for i, lbl in enumerate(self.lap_labels):
            lbl.config(text=f"{i+1}. {self.lap_times[i]}" if i < len(self.lap_times) else "--:--.---")

    def format_time(self, seconds, force_positive=False):
        sign = ""
        if seconds < 0 and not force_positive:
            sign = "-"
            seconds = -seconds
            
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        millis = int((seconds * 1000) % 1000)
        return f"{sign}{mins:02}:{secs:02}.{millis:03}"

    def update_timer(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            if self.preset_duration is not None:
                remaining = self.preset_duration - self.elapsed_time
                self.time_label.config(text=self.format_time(remaining))
            else:
                self.time_label.config(text=self.format_time(self.elapsed_time))
        self.root.after(10, self.update_timer)

    def beep(self, start=True):
        def _beep():
            winsound.Beep(600 if start else 300, 150 if start else 300)
        threading.Thread(target=_beep, daemon=True).start()
    def start_listening(self):
        self.stop_listening()
        
        t = self.bind_config['type']
        v = self.bind_config['value']
        
        try:
            if t == 'keyboard':
                self.hook = keyboard.on_press_key(v, lambda e: self.root.after(0, self.toggle_timer))
            elif t == 'mouse':
                self.hook = mouse.on_button(lambda: self.root.after(0, self.toggle_timer), buttons=(v,), types=(mouse.DOWN,))
        except Exception as e:
            print(f"Error binding {t} {v}: {e}")
            
    def stop_listening(self):
        try:
            keyboard.unhook_all()
            mouse.unhook_all()
        except:
            pass

    def change_bind_mode(self):
        self.stop_listening()
        self.instr.config(text="Press NEW Key or Mouse Button...", fg="#ffff00")
        self.root.update()
        threading.Thread(target=self.wait_for_input, daemon=True).start()

    def wait_for_input(self):
        found_event = None
        def k_hook(e):
            nonlocal found_event
            if e.event_type == 'down' and not found_event:
                found_event = {'type': 'keyboard', 'value': e.name}
        def m_hook(e):
            nonlocal found_event
            if isinstance(e, mouse.ButtonEvent) and e.event_type == 'down' and not found_event:
                found_event = {'type': 'mouse', 'value': e.button}
        try:
            keyboard.hook(k_hook)
            mouse.hook(m_hook)
            while not found_event:
                time.sleep(0.05)
            self.bind_config = found_event
            self.save_config()
            self.root.after(0, self.finish_binding)
            
        finally:
            keyboard.unhook_all()
            mouse.unhook_all()

    def set_opacity(self, value):
        self.ui_config['opacity'] = value
        self.root.wm_attributes("-alpha", value)
        self.save_config()

    def set_window_size(self, size_str):
        self.ui_config['size'] = size_str
        self.root.geometry(size_str)
        self.save_config()

    def change_text_color(self):
        colors = ["#00ff00", "#ff0000", "#0000ff", "#ffff00", "#00ffff", "#ff00ff", "#ffffff"]
        current = self.ui_config.get('text_color', "#00ff00")
        try:
            next_index = (colors.index(current) + 1) % len(colors)
        except ValueError:
            next_index = 0
        new_color = colors[next_index]
        
        self.ui_config['text_color'] = new_color
        self.text_color = new_color
        self.time_label.config(fg=new_color)
        self.save_config()

    def ask_color(self):
        self.change_text_color()
            
    def finish_binding(self):
        self.instr.config(text=self.get_bind_text(), fg="#888888")
        self.start_listening()

if __name__ == "__main__":
    root = tk.Tk()
    app = RacingTimer(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
