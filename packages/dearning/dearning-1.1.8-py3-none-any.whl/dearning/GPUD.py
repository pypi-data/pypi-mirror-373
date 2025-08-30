import time, threading, inspect, builtins, sys, os, curses
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

try:
    import arrayfire as af
    GPU_AVAILABLE = True
    DEVICE_INFO = af.info()
    af.set_backend('opencl')  # fallback otomatis jika CUDA tidak ada
except ImportError:
    GPU_AVAILABLE = False
    DEVICE_INFO = "ArrayFire tidak tersedia. Gunakan pip install arrayfire"

def use_gpu_conditionally(data_size=10000):
    return GPU_AVAILABLE and data_size > 5000

def af_array(x):
    if GPU_AVAILABLE:
        return af.np_to_af_array(x)
    return x

def gpu_dot(x, y):
    if GPU_AVAILABLE:
        return af.dot(x, y)
    else:
        import numpy as np
        return np.dot(x, y)

def gpu_add(x, y):
    if GPU_AVAILABLE:
        return af.add(x, y)
    else:
        return x + y

def gpu_mean(x):
    if GPU_AVAILABLE:
        return af.mean(x)
    else:
        import numpy as np
        return np.mean(x)

def gpu_info():
    return DEVICE_INFO if GPU_AVAILABLE else "GPU tidak aktif"

def is_gpu_on():
    return GPU_AVAILABLE

# === GUI Terminal Interaktif ===
console = Console()

class TerminalGuiTool:
    def __init__(self):
        self.lines = []
        self.title = "📺 Terminal GUI"
        self.help_text = "Tekan q untuk keluar. Tekan a untuk tambah baris."

    def add_line(self, content: str):
        self.lines.append(content)

    def set_title(self, title: str):
        self.title = title

    def set_help(self, help_text: str):
        self.help_text = help_text

    def run_gui(self):
        curses.wrapper(self._main_loop)

    def _main_loop(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        while True:
            stdscr.clear()
            title_panel = Panel(Text(self.title, style="bold green"))
            console.print(title_panel)

            for i, line in enumerate(self.lines):
                text = Text(line, style="white")
                console.print(text)

            console.print(Panel(Text(self.help_text, style="dim cyan")))

            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('a'):
                self.add_line("✨ Baris tambahan!")

            stdscr.refresh()

# === Dearning Processing Unit ===
class DearningProcessingUnit:
    _enabled = False
    _start_time = None
    _line_threshold = 450

    @classmethod
    def enable(cls):
        cls._enabled = True
        cls._start_time = time.time()
        print("⚡ Dearning Processing Unit diaktifkan...")

        monitor = threading.Thread(target=cls._monitor_usage)
        monitor.daemon = True
        monitor.start()

    @classmethod
    def _monitor_usage(cls):
        time.sleep(1)
        current_script = sys.argv[0]
        if not os.path.exists(current_script):
            return

        try:
            with open(current_script, 'r') as f:
                lines = f.readlines()
                total_lines = len(lines)
        except Exception as e:
            print("❌ Gagal membaca script:", e)
            return

        print(f"📏 Total baris kode: {total_lines}")

        if total_lines > cls._line_threshold:
            print("⚙️ Kode panjang terdeteksi. Mengaktifkan optimasi...")
            cls._optimize_for_low_device()

    @classmethod
    def _optimize_for_low_device(cls):
        builtins.print = cls._light_print
        os.environ["DEARNING_OPTIMIZED"] = "1"

    @staticmethod
    def _light_print(*args, **kwargs):
        msg = " ".join(str(a) for a in args)
        if "✅" in msg or "❌" in msg or "⚠️" in msg:
            builtins.__dict__["print"](msg, **kwargs)

# Alias
Dpu = DearningProcessingUnit