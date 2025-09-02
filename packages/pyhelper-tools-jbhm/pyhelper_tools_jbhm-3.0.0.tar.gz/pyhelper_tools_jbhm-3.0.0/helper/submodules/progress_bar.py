from .shared import time,tk, Canvas, timedelta,  Optional
from .timer import Timer

class ProgressBar:
    def __init__(self, total: int, desc: str = "Progreso", 
                 bar_length: int = 40, auto_start: bool = True, 
                 timer: Optional[Timer] = None, parent_window=None):
        self.total = total
        self.desc = desc
        self.bar_length = bar_length
        self.current = 0
        self.timer = Timer() if timer is None else timer
        self.eta = 0
        self.eta_formatted = "00:00:00"
        self.last_update_time = 0
        self.update_interval = 0.1
        

        self.window = tk.Toplevel() if parent_window is None else parent_window
        self.window.title(desc)
        self.window.geometry("600x200")
        self.window.resizable(False, False)
        self.window.configure(bg='#f0f0f0')
        

        self.dark_mode = False
        self.colors = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'accent': '#007acc',
            'secondary': '#e0e0e0',
            'progress_bg': '#d0d0d0'
        }
        
        self._create_widgets()
        
        if auto_start:
            self.timer.start()
            self._update_display()
    
    def _create_widgets(self):

        main_frame = tk.Frame(self.window, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        

        self.desc_var = tk.StringVar(value=self.desc)
        desc_font = ("Arial", 12, "bold")
        self.desc_label = tk.Label(main_frame, textvariable=self.desc_var, 
                                  font=desc_font, bg=self.colors['bg'], fg=self.colors['fg'])
        self.desc_label.pack(anchor=tk.W, pady=(0, 10))
        

        self.canvas = Canvas(main_frame, height=30, bg=self.colors['bg'], 
                            highlightthickness=0)
        self.canvas.pack(fill=tk.X, pady=5)
        

        self.info_var = tk.StringVar(value="0/0 (0.0%) | ETA: 00:00:00 | Elapsed: 00:00:00")
        self.info_label = tk.Label(main_frame, textvariable=self.info_var,
                                  bg=self.colors['bg'], fg=self.colors['fg'])
        self.info_label.pack(anchor=tk.W, pady=5)
        

        self.theme_btn = tk.Button(main_frame, text="🌙", command=self.toggle_theme,
                                  bg=self.colors['secondary'], fg=self.colors['fg'],
                                  relief=tk.FLAT, font=("Arial", 12))
        self.theme_btn.pack(side=tk.BOTTOM, anchor=tk.E, pady=5)
        

        self._draw_progress_bar()
    
    def _draw_progress_bar(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        if width < 10:  # Si el canvas aún no tiene tamaño
            width = 500
        

        self.canvas.create_rectangle(0, 0, width, 30, 
                                    fill=self.colors['progress_bg'], outline="")
        

        progress = min(1.0, self.current / self.total)
        progress_width = int(width * progress)
        
        if progress_width > 0:

            self.canvas.create_rectangle(0, 0, progress_width, 30, 
                                        fill=self.colors['accent'], outline="")
            

            if progress_width < width:
                self.canvas.create_arc(progress_width-15, 0, progress_width+15, 30, 
                                      start=270, extent=180, fill=self.colors['accent'], outline="")
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.colors = {
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'accent': '#4ec9b0',
                'secondary': '#3d3d3d',
                'progress_bg': '#3d3d3d'
            }
            self.theme_btn.config(text="☀️")
        else:
            self.colors = {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'accent': '#007acc',
                'secondary': '#e0e0e0',
                'progress_bg': '#d0d0d0'
            }
            self.theme_btn.config(text="🌙")
        

        self.window.configure(bg=self.colors['bg'])
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors['bg'])
        
        self.desc_label.configure(bg=self.colors['bg'], fg=self.colors['fg'])
        self.info_label.configure(bg=self.colors['bg'], fg=self.colors['fg'])
        self.canvas.configure(bg=self.colors['bg'])
        self.theme_btn.configure(bg=self.colors['secondary'], fg=self.colors['fg'])
        
        self._draw_progress_bar()
    
    def update(self, n: int = 1, metrics: Optional[dict] = None):
        self.current += n
        
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval or self.current >= self.total:
            self._calculate_eta()
            self.last_update_time = current_time
        
        self._update_display(metrics)
    
    def _calculate_eta(self):
        if self.current == 0:
            self.eta = 0
            self.eta_formatted = "00:00:00"
            return
        
        elapsed = self.timer.get_elapsed_time()
        if elapsed > 0:
            rate = self.current / elapsed
            if rate > 0:
                remaining = self.total - self.current
                self.eta = remaining / rate
                self.eta_formatted = str(timedelta(seconds=int(self.eta)))
    
    def _update_display(self, metrics: Optional[dict] = None):
        progress = min(1.0, self.current / self.total)
        

        resources_info = ""
        if metrics:
            resources_info = f" | CPU: {metrics.get('cpu', 0):.1f}% | RAM: {metrics.get('ram', 0):.1f}%"
            if metrics.get('gpu_info', {}).get('monitorable', False):
                resources_info += f" | GPU: {metrics.get('gpu', 0):.1f}%"
            resources_info += f" | Power: {metrics.get('power', 0):.1f}W"
        

        self.info_var.set(f"{self.current}/{self.total} ({progress*100:.1f}%) | "
                         f"ETA: {self.eta_formatted} | "
                         f"Elapsed: {self.timer.get_formatted_time()}{resources_info}")
        

        self._draw_progress_bar()
        

        if self.current < self.total:
            self.window.after(int(self.update_interval * 1000), 
                             lambda: self._update_display(metrics))
    
    def close(self):
        self.window.destroy()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
