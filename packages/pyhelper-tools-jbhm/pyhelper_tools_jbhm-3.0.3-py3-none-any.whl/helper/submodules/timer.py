from .shared import time, tk, timedelta, Optional

class Timer:
    def __init__(self, parent_window=None):
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0
        self.paused: bool = False
        self.pause_start: Optional[float] = None
        

        self.window = tk.Toplevel() if parent_window is None else parent_window
        self.window.title("Timer")
        self.window.geometry("350x200")
        self.window.resizable(False, False)
        self.window.configure(bg='#f0f0f0')
        

        self.dark_mode = False
        self.colors = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'accent': '#007acc',
            'secondary': '#e0e0e0'
        }
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):

        main_frame = tk.Frame(self.window, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        

        self.time_var = tk.StringVar(value="00:00:00")
        time_font = ("Arial", 32, "bold")
        self.time_label = tk.Label(main_frame, textvariable=self.time_var, 
                                  font=time_font, bg=self.colors['bg'], fg=self.colors['accent'])
        self.time_label.pack(pady=10)
        

        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.pack(pady=10)
        

        self.start_btn = tk.Button(btn_frame, text="Start", command=self.start,
                                  bg=self.colors['secondary'], fg=self.colors['fg'],
                                  relief=tk.FLAT, padx=15, pady=5)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(btn_frame, text="Pause", command=self.pause, state=tk.DISABLED,
                                  bg=self.colors['secondary'], fg=self.colors['fg'],
                                  relief=tk.FLAT, padx=15, pady=5)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset,
                                  bg=self.colors['secondary'], fg=self.colors['fg'],
                                  relief=tk.FLAT, padx=15, pady=5)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        

        self.theme_btn = tk.Button(main_frame, text="🌙", command=self.toggle_theme,
                                  bg=self.colors['secondary'], fg=self.colors['fg'],
                                  relief=tk.FLAT, font=("Arial", 12))
        self.theme_btn.pack(side=tk.BOTTOM, pady=5)
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.colors = {
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'accent': '#4ec9b0',
                'secondary': '#3d3d3d'
            }
            self.theme_btn.config(text="☀️")
        else:
            self.colors = {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'accent': '#007acc',
                'secondary': '#e0e0e0'
            }
            self.theme_btn.config(text="🌙")
        

        self.window.configure(bg=self.colors['bg'])
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors['bg'])
        
        self.time_label.configure(bg=self.colors['bg'], fg=self.colors['accent'])
        
        for btn in [self.start_btn, self.pause_btn, self.reset_btn, self.theme_btn]:
            btn.configure(bg=self.colors['secondary'], fg=self.colors['fg'])
    
    def start(self):
        if self.paused and self.pause_start is not None:
            pause_duration = time.time() - self.pause_start
            self.start_time += pause_duration
            self.paused = False
            self.pause_start = None
        elif self.start_time is None:
            self.start_time = time.time()
            self.paused = False
        
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
    
    def pause(self):
        if not self.paused and self.start_time is not None:
            self.paused = True
            self.pause_start = time.time()
            self.elapsed_time = self.pause_start - self.start_time
        
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
    
    def reset(self):
        self.start_time = None
        self.elapsed_time = 0
        self.paused = False
        self.pause_start = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self._update_display()
    
    def get_elapsed_time(self) -> float:
        if self.paused:
            return self.elapsed_time
        elif self.start_time is not None:
            return time.time() - self.start_time
        else:
            return 0
    
    def get_formatted_time(self) -> str:
        elapsed = self.get_elapsed_time()
        return str(timedelta(seconds=int(elapsed)))
    
    def is_running(self) -> bool:
        return self.start_time is not None and not self.paused
    
    def _update_display(self):
        elapsed = self.get_elapsed_time()
        formatted = str(timedelta(seconds=int(elapsed)))
        self.time_var.set(formatted)
        
        if self.is_running():
            self.window.after(1000, self._update_display)
