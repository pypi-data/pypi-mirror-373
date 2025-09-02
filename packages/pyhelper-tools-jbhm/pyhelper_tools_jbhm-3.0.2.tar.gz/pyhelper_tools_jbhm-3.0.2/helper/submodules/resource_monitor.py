from .shared import time, tk, Canvas, Tuple, psutil, threading, subprocess, platform, Dict, List, ilu

class ResourceMonitor:
    def __init__(self, update_interval: float = 1.0, parent_window=None):
        self.update_interval = update_interval
        self.cpu_usage = 0.0
        self.ram_usage = 0.0
        self.gpu_info = self._detect_gpu()
        self.gpu_usage = 0.0
        self.gpu_memory = 0.0
        self.power_usage = 0.0
        self.running = False
        self.thread = None

        self.amd_monitor = None

        if platform.system() == "Windows" and self.gpu_info["vendor"] == "amd":
            self.amd_monitor = _WindowsAMDMonitor_()
            self.gpu_info["monitorable"] = self.amd_monitor.monitorable


        self.window = tk.Toplevel() if parent_window is None else parent_window
        self.window.title("Resource Monitor")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.configure(bg="#f0f0f0")


        self.dark_mode = False
        self.colors = {
            "bg": "#f0f0f0",
            "fg": "#000000",
            "accent": "#007acc",
            "secondary": "#e0e0e0",
            "gpu_accent": "#ff6b6b",
            "ram_accent": "#51cf66",
            "power_accent": "#fcc419",
        }

        self._create_widgets()

    def _check_amd_support(self) -> bool:
        """
        Checks if AMD monitoring support is available on the current operating system.
        Combines multiple detection methods for greater robustness.

        Returns:
        bool: True if support is detected, False otherwise.
        """
        try:
            system = platform.system().lower()
        

            if system == "windows":

                try:
                    result = subprocess.run(
                        ["wmic", "path", "Win32_VideoController", "get", "Name"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0 and ("AMD" in result.stdout.upper() or "Radeon" in result.stdout.upper()):
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
            

                try:
                    if ilu.find_spec("pyadl") is not None:
                        return True
                except ImportError:
                    pass
                

                try:
                    ps_cmd = [
                        "powershell",
                        "-Command",
                        "Get-WmiObject -Class Win32_VideoController | Where-Object {$_.Name -like '*AMD*' -or $_.Name -like '*Radeon*'} | Select-Object -ExpandProperty Name"
                    ]
                    result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                    
                return False


            elif system == "linux":

                try:
                    result = subprocess.run(
                        ["which", "rocm-smi"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():

                        rocm_result = subprocess.run(
                            ["rocm-smi", "--showproductname"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=5
                        )
                        if rocm_result.returncode == 0:
                            return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass


                try:
                    result = subprocess.run(
                        ["which", "radeontop"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                    

                try:
                    result = subprocess.run(
                        ["lspci"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and ("AMD" in result.stdout or "Radeon" in result.stdout):
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                    
                return False


            elif system == "darwin":

                try:
                    result = subprocess.run(
                        ["system_profiler", "SPDisplaysDataType"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0 and ("AMD" in result.stdout or "Radeon" in result.stdout):
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                

                try:
                    result = subprocess.run(
                        ["system_profiler", "-xml", "SPDisplaysDataType"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=10
                    )
                    if result.returncode == 0:

                        if b"AMD" in result.stdout or b"Radeon" in result.stdout:
                            return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                
                return False


            else:

                try:

                    result = subprocess.run(
                        ["which", "lspci"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:

                        lspci_result = subprocess.run(
                            ["lspci"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=5
                        )
                        if lspci_result.returncode == 0 and ("AMD" in lspci_result.stdout or "Radeon" in lspci_result.stdout):
                            return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                
                return False

        except Exception as e:


            return False


    def _create_widgets(self):

        main_frame = tk.Frame(self.window, bg=self.colors["bg"], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)


        title_font = ("Arial", 16, "bold")
        title_label = tk.Label(
            main_frame,
            text="Monitor de Recursos",
            font=title_font,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        )
        title_label.pack(pady=(0, 20))


        cpu_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        cpu_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            cpu_frame,
            text="CPU:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10),
        ).pack(side=tk.LEFT)

        self.cpu_var = tk.StringVar(value="0.0%")
        tk.Label(
            cpu_frame,
            textvariable=self.cpu_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10, "bold"),
        ).pack(side=tk.RIGHT)

        self.cpu_canvas = Canvas(
            cpu_frame, height=20, bg=self.colors["bg"], highlightthickness=0
        )
        self.cpu_canvas.pack(fill=tk.X, pady=2)


        ram_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        ram_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            ram_frame,
            text="RAM:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10),
        ).pack(side=tk.LEFT)

        self.ram_var = tk.StringVar(value="0.0%")
        tk.Label(
            ram_frame,
            textvariable=self.ram_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10, "bold"),
        ).pack(side=tk.RIGHT)

        self.ram_canvas = Canvas(
            ram_frame, height=20, bg=self.colors["bg"], highlightthickness=0
        )
        self.ram_canvas.pack(fill=tk.X, pady=2)


        gpu_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        gpu_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            gpu_frame,
            text="GPU:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10),
        ).pack(side=tk.LEFT)

        self.gpu_var = tk.StringVar(value="0.0%")
        tk.Label(
            gpu_frame,
            textvariable=self.gpu_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10, "bold"),
        ).pack(side=tk.RIGHT)

        self.gpu_canvas = Canvas(
            gpu_frame, height=20, bg=self.colors["bg"], highlightthickness=0
        )
        self.gpu_canvas.pack(fill=tk.X, pady=2)


        gpu_mem_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        gpu_mem_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            gpu_mem_frame,
            text="GPU Memory:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10),
        ).pack(side=tk.LEFT)

        self.gpu_mem_var = tk.StringVar(value="0.0%")
        tk.Label(
            gpu_mem_frame,
            textvariable=self.gpu_mem_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10, "bold"),
        ).pack(side=tk.RIGHT)

        self.gpu_mem_canvas = Canvas(
            gpu_mem_frame, height=20, bg=self.colors["bg"], highlightthickness=0
        )
        self.gpu_mem_canvas.pack(fill=tk.X, pady=2)


        power_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        power_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            power_frame,
            text="Power:",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10),
        ).pack(side=tk.LEFT)

        self.power_var = tk.StringVar(value="0.0W")
        tk.Label(
            power_frame,
            textvariable=self.power_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 10, "bold"),
        ).pack(side=tk.RIGHT)

        self.power_canvas = Canvas(
            power_frame, height=20, bg=self.colors["bg"], highlightthickness=0
        )
        self.power_canvas.pack(fill=tk.X, pady=2)


        self.theme_btn = tk.Button(
            main_frame,
            text="🌙",
            command=self.toggle_theme,
            bg=self.colors["secondary"],
            fg=self.colors["fg"],
            relief=tk.FLAT,
            font=("Arial", 12),
        )
        self.theme_btn.pack(side=tk.BOTTOM, anchor=tk.E, pady=10)


        self._draw_bars()

    def _detect_gpu(self) -> Dict[str, str]:
        """Detecta el tipo de GPU disponible según el sistema operativo"""
        system = platform.system()
        gpu_info = {
            "type": "generic",
            "vendor": "unknown",
            "model": "GPU Genérica no monitoreable",
            "monitorable": False,
        }


        if system == "Windows":
            return self._detect_gpu_windows()


        elif system == "Linux":
            return self._detect_gpu_linux()


        elif system == "Darwin":
            return self._detect_gpu_macos()

        return gpu_info

    def _detect_gpu_linux(self) -> Dict[str, str]:
        """Detección de GPU para Linux"""
        gpu_info = {
            "type": "generic",
            "vendor": "unknown",
            "model": "GPU Genérica no monitoreable",
            "monitorable": False,
        }


        try:
            import pynvml

            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    gpu_info["vendor"] = "nvidia"
                    gpu_info["model"] = pynvml.nvmlDeviceGetName(handle).decode("utf-8")
                    gpu_info["monitorable"] = True
                    gpu_info["type"] = "dedicated"
                pynvml.nvmlShutdown()
                return gpu_info
            except Exception:
                pass
        except ImportError:
            pass


        try:

            if platform.system() == "Linux":
                import pyamdgpuinfo

                if pyamdgpuinfo.detect_gpus() > 0:
                    gpu_info["vendor"] = "amd"
                    gpu_info["model"] = "AMD GPU"
                    gpu_info["monitorable"] = True
                    gpu_info["type"] = "dedicated"
                    return gpu_info
        except ImportError:
            pass


        lspci_output = self._get_lspci_output()
        if "intel" in platform.processor().lower() or any(
            "intel" in line.lower() for line in lspci_output
        ):
            gpu_info["vendor"] = "intel"
            gpu_info["model"] = "Intel Integrated Graphics"
            gpu_info["type"] = "integrated"

            gpu_info["monitorable"] = False

        return gpu_info

    def _detect_gpu_macos(self) -> Dict[str, str]:
        """Detección de GPU para macOS"""
        gpu_info = {
            "type": "generic",
            "vendor": "unknown",
            "model": "GPU Genérica no monitoreable",
            "monitorable": False,
        }

        try:
            import subprocess

            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                if "nvidia" in output:
                    gpu_info["vendor"] = "nvidia"
                elif "amd" in output or "radeon" in output:
                    gpu_info["vendor"] = "amd"
                elif "intel" in output:
                    gpu_info["vendor"] = "intel"
                    gpu_info["type"] = "integrated"


                lines = result.stdout.split("\n")
                for i, line in enumerate(lines):
                    if "chipset model" in line.lower():
                        gpu_info["model"] = line.split(":")[-1].strip()
                        break
        except Exception:
            pass

        return gpu_info

    def _detect_gpu_windows(self) -> Dict[str, str]:
        """Detección de GPU para Windows con mejor soporte para AMD"""
        gpu_info = {
            "type": "generic",
            "vendor": "unknown",
            "model": "GPU Genérica no monitoreable",
            "monitorable": False,
        }


        nvidia_detected = False
        try:
            import pynvml

            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    gpu_info["vendor"] = "nvidia"
                    gpu_info["model"] = pynvml.nvmlDeviceGetName(handle).decode("utf-8")
                    gpu_info["monitorable"] = True
                    gpu_info["type"] = "dedicated"
                    nvidia_detected = True
                pynvml.nvmlShutdown()
            except Exception:
                pass
        except ImportError:
            pass


        if not nvidia_detected:
            try:

                import wmi

                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    if (
                        gpu.Name
                        and "Microsoft" not in gpu.Name
                        and "Basic" not in gpu.Name
                    ):
                        gpu_name = gpu.Name
                        gpu_info["model"] = gpu_name

                        if any(
                            keyword in gpu_name.lower()
                            for keyword in ["nvidia", "geforce", "rtx", "gtx"]
                        ):
                            gpu_info["vendor"] = "nvidia"
                        elif any(
                            keyword in gpu_name.lower()
                            for keyword in ["amd", "radeon", "rx"]
                        ):
                            gpu_info["vendor"] = "amd"

                            gpu_info["monitorable"] = self._check_amd_support()
                        elif "intel" in gpu_name.lower():
                            gpu_info["vendor"] = "intel"
                            gpu_info["type"] = "integrated"

                        break
            except ImportError:

                try:
                    import subprocess

                    result = subprocess.run(
                        [
                            "powershell",
                            "Get-WmiObject -Class Win32_VideoController | Select-Object -ExpandProperty Name",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        gpu_name = result.stdout.strip().split("\n")[0]
                        gpu_info["model"] = gpu_name
                        if any(
                            keyword in gpu_name.lower()
                            for keyword in ["nvidia", "geforce", "rtx", "gtx"]
                        ):
                            gpu_info["vendor"] = "nvidia"
                        elif any(
                            keyword in gpu_name.lower()
                            for keyword in ["amd", "radeon", "rx"]
                        ):
                            gpu_info["vendor"] = "amd"
                            gpu_info["monitorable"] = self._check_amd_support()
                        elif "intel" in gpu_name.lower():
                            gpu_info["vendor"] = "intel"
                            gpu_info["type"] = "integrated"
                except Exception:
                    pass

        return gpu_info

    def _draw_bars(self):
        for canvas, usage, color in [
            (self.cpu_canvas, self.cpu_usage, self.colors["accent"]),
            (self.ram_canvas, self.ram_usage, self.colors["ram_accent"]),
            (self.gpu_canvas, self.gpu_usage, self.colors["gpu_accent"]),
            (self.gpu_mem_canvas, self.gpu_memory, self.colors["gpu_accent"]),
            (
                self.power_canvas,
                min(self.power_usage / 200 * 100, 100),
                self.colors["power_accent"],
            ),
        ]:
            self._draw_curved_bar(canvas, usage, color)

    def _draw_curved_bar(self, canvas, usage, color):
        canvas.delete("all")
        width = canvas.winfo_width()
        if width < 10:  # Si el canvas aún no tiene tamaño
            width = 400


        canvas.create_rectangle(0, 5, width, 15, fill="#d0d0d0", outline="")


        progress_width = int(width * usage / 100)

        if progress_width > 0:

            canvas.create_rectangle(
                0, 5, progress_width, 15, fill=color, outline=""
            )


            if progress_width < width:
                canvas.create_arc(
                    progress_width - 10,
                    5,
                    progress_width + 10,
                    15,
                    start=270,
                    extent=180,
                    fill=color,
                    outline="",
                )

    def _estimate_power_usage_(self):
        """Estima el consumo de energía basado en el uso de CPU y GPU, calibrado por tipo de hardware."""


        estimated_tdp = 65  # Valor por defecto para desktop, en Watts
    
        try:

            if ilu.find_spec("cpuinfo") is not None:
                import cpuinfo
                info = cpuinfo.get_cpu_info()
                brand = info.get("brand_raw", "").lower()


                if "intel" in brand:
                    if "mobile" in brand or "u" in brand or "y" in brand:
                        estimated_tdp = 15
                    elif "xeon" in brand or "i9" in brand:
                        estimated_tdp = 95
                    else:
                        estimated_tdp = 65
                elif "amd" in brand:
                    if "ryzen 9" in brand or "threadripper" in brand:
                        estimated_tdp = 105
                    elif "ryzen 7" in brand:
                        estimated_tdp = 65
                    else:
                        estimated_tdp = 45
                else:
                    estimated_tdp = 50

        except Exception:
            pass


        base_cpu_draw = estimated_tdp * 0.20


        cpu_power = base_cpu_draw + (estimated_tdp - base_cpu_draw) * (self.cpu_usage / 100.0)


        if self.gpu_info.get("monitorable", False):


            estimated_gpu_tdp = self.gpu_info.get("tdp", 150)
            gpu_power = (estimated_gpu_tdp * (self.gpu_usage / 100.0))
        else:
            gpu_power = 0


        self.power_usage = cpu_power + gpu_power

    def _get_lspci_output(self) -> List[str]:
        """Obtiene la salida de lspci (solo Linux)"""
        try:
            if platform.system() == "Linux":
                import subprocess

                result = subprocess.run(
                    ["lspci"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.split("\n")
        except Exception:
            pass
        return []

    def _monitoring_loop(self):
        """Bucle principal de monitoreo"""
        while self.running:
            self._update_metrics()
            time.sleep(self.update_interval)

    def _update_gpu_metrics(self):
        """Actualiza las métricas de GPU según el vendor"""
        try:
            if self.gpu_info["vendor"] == "nvidia":
                import pynvml

                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)


                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                self.gpu_usage = utilization.gpu


                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                self.gpu_memory = memory.used / memory.total * 100

                pynvml.nvmlShutdown()

            elif self.gpu_info["vendor"] == "amd":
                if platform.system() == "Linux":

                    try:
                        import pyamdgpuinfo

                        gpu = pyamdgpuinfo.getGPU(0)
                        self.gpu_usage = gpu.query_load() * 100
                        self.gpu_memory = (
                            gpu.query_vram_usage() / gpu.memory_info["vram_size"] * 100
                        )
                    except ImportError:
                        self.gpu_info["monitorable"] = False

                elif platform.system() == "Windows" and self.amd_monitor:

                    self.amd_monitor.update_metrics()
                    self.gpu_usage = self.amd_monitor.gpu_usage
                    self.gpu_memory = self.amd_monitor.gpu_memory

            elif self.gpu_info["vendor"] == "intel":

                self.gpu_usage = 0.0
                self.gpu_memory = 0.0

        except Exception as e:
            self.gpu_info["monitorable"] = False
            self.gpu_info["model"] = f"Error monitoring {self.gpu_info['vendor'].upper()} GPU"

    def _update_metrics(self):
        """Actualiza las métricas del sistema"""

        self.cpu_usage = psutil.cpu_percent(interval=None)


        ram = psutil.virtual_memory()
        self.ram_usage = ram.percent


        if self.gpu_info["monitorable"]:
            self._update_gpu_metrics()


        self._estimate_power_usage_()

    def get_metrics(self) -> Dict[str, float]:
        """Devuelve todas las métricas actuales"""
        return {
            "cpu": self.cpu_usage,
            "ram": self.ram_usage,
            "gpu": self.gpu_usage,
            "gpu_memory": self.gpu_memory,
            "power": self.power_usage,
            "gpu_info": self.gpu_info,
        }

    def start(self):
        """Inicia el monitoreo en un hilo separado"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitoring_loop)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """Detiene el monitoreo"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.colors = {
                "bg": "#2d2d2d",
                "fg": "#ffffff",
                "accent": "#4ec9b0",
                "secondary": "#3d3d3d",
                "gpu_accent": "#ff6b6b",
                "ram_accent": "#51cf66",
                "power_accent": "#fcc419",
            }
            self.theme_btn.config(text="☀️")
        else:
            self.colors = {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "accent": "#007acc",
                "secondary": "#e0e0e0",
                "gpu_accent": "#ff6b6b",
                "ram_accent": "#51cf66",
                "power_accent": "#fcc419",
            }
            self.theme_btn.config(text="🌙")


        self.window.configure(bg=self.colors["bg"])
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors["bg"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=self.colors["bg"], fg=self.colors["fg"])

        for canvas in [
            self.cpu_canvas,
            self.ram_canvas,
            self.gpu_canvas,
            self.gpu_mem_canvas,
            self.power_canvas,
        ]:
            canvas.configure(bg=self.colors["bg"])

        self.theme_btn.configure(bg=self.colors["secondary"], fg=self.colors["fg"])

        self._draw_bars()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class _WindowsAMDMonitor_:
    """
    Specialized monitor for AMD GPUs on Windows.
    Uses tools accessible without elevated permissions.
    If errors are detected, it returns metrics of 0 and marks it as unmonitorable.
    """

    def __init__(self):
        self.running = False
        self.gpu_usage = 0.0
        self.gpu_memory = 0.0
        self.monitorable = self._check_amd_support()
        self.last_update = 0
        self.update_interval = 1

    def _check_amd_support(self) -> bool:
        """
        Checks if AMD monitoring support is available on the current operating system.
        Combines multiple detection methods for greater robustness.

        Returns:
        bool: True if support is detected, False otherwise.
        """
        try:
            system = platform.system().lower()
        

            if system == "windows":

                try:
                    result = subprocess.run(
                        ["wmic", "path", "Win32_VideoController", "get", "Name"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0 and ("AMD" in result.stdout.upper() or "Radeon" in result.stdout.upper()):
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
            

                try:
                    if ilu.find_spec("pyadl") is not None:
                        return True
                except ImportError:
                    pass
                

                try:
                    ps_cmd = [
                        "powershell",
                        "-Command",
                        "Get-WmiObject -Class Win32_VideoController | Where-Object {$_.Name -like '*AMD*' -or $_.Name -like '*Radeon*'} | Select-Object -ExpandProperty Name"
                    ]
                    result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                    
                return False


            elif system == "linux":

                try:
                    result = subprocess.run(
                        ["which", "rocm-smi"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():

                        rocm_result = subprocess.run(
                            ["rocm-smi", "--showproductname"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=5
                        )
                        if rocm_result.returncode == 0:
                            return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass


                try:
                    result = subprocess.run(
                        ["which", "radeontop"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                    

                try:
                    result = subprocess.run(
                        ["lspci"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and ("AMD" in result.stdout or "Radeon" in result.stdout):
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                    
                return False


            elif system == "darwin":

                try:
                    result = subprocess.run(
                        ["system_profiler", "SPDisplaysDataType"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0 and ("AMD" in result.stdout or "Radeon" in result.stdout):
                        return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                

                try:
                    result = subprocess.run(
                        ["system_profiler", "-xml", "SPDisplaysDataType"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=10
                    )
                    if result.returncode == 0:

                        if b"AMD" in result.stdout or b"Radeon" in result.stdout:
                            return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                
                return False


            else:

                try:

                    result = subprocess.run(
                        ["which", "lspci"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:

                        lspci_result = subprocess.run(
                            ["lspci"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=5
                        )
                        if lspci_result.returncode == 0 and ("AMD" in lspci_result.stdout or "Radeon" in lspci_result.stdout):
                            return True
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
                
                return False

        except Exception as e:


            return False

    def _get_gpu_usage(self) -> float:
        """Obtiene el uso de la GPU AMD"""
        try:
            cmd = [
                "powershell",
                "-Command",
                "(Get-Counter '\\GPU Engine(*)\\Utilization Percentage').CounterSamples | "
                "Where-Object {$_.InstanceName -like '*engtype_3D*'} | "
                "Measure-Object -Property CookedValue -Average | "
                "Select-Object -ExpandProperty Average"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            usage_str = result.stdout.strip()
            return float(usage_str) if usage_str and usage_str != "" else 0.0
        except Exception:
            return 0.0

    def _get_gpu_memory(self) -> Tuple[float, float]:
        """Obtiene el uso de memoria de la GPU AMD (devuelve (uso, total))"""
        try:

            cmd = [
                "wmic", "path", "Win32_VideoController", "get", 
                "AdapterRAM,CurrentHorizontalResolution,CurrentVerticalResolution"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "AMD" in line or "Radeon" in line:
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        total_vram = float(parts[0]) / (1024 * 1024)

                        usage = total_vram * 0.3
                        return usage, total_vram
            
            return 0.0, 0.0
        except Exception:
            return 0.0, 0.0

    def update_metrics(self):
        """Actualiza las métricas de la GPU AMD en Windows."""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        self.last_update = current_time
        
        if not self.monitorable:
            self.gpu_usage = 0.0
            self.gpu_memory = 0.0
            return
        
        try:

            self.gpu_usage = self._get_gpu_usage()
            

            memory_usage, total_memory = self._get_gpu_memory()
            if total_memory > 0:
                self.gpu_memory = (memory_usage / total_memory) * 100
            else:
                self.gpu_memory = 0.0
                
        except Exception as e:
            self.gpu_usage = 0.0
            self.gpu_memory = 0.0
            print(f"Exception in resource monitor: {e}")
