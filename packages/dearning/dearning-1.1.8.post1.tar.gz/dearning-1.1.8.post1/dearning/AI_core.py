import inspect, ast, binascii, sys, traceback, os, time, logging, subprocess, json, threading, builtins
from collections import deque
from pathlib import Path
from dearning import Quantum

try:
    import numpy as np
except ImportError:
    np = None  # Pastikan numpy terinstall untuk fitur advanced

class CodeTracker:
    def __init__(self):
        self._logs = []

    def __call__(self, func):
        """Memungkinkan dekorator @tracker digunakan langsung."""
        return self._wrap(func)

    def log_function_call(self, func):
        """Memungkinkan dekorator @tracker.log_function_call."""
        return self._wrap(func)

    def _wrap(self, func):
        """Logik dekorator yang digunakan oleh __call__ dan log_function_call."""
        def wrapper(*args, **kwargs):
            self._logs.append(f"▶️ {func.__name__}() dipanggil.")
            result = func(*args, **kwargs)
            self._logs.append(f"✅ {func.__name__} selesai. → {result}")
            return result
        return wrapper

    def get(self):
        """Mengembalikan salinan log saat ini."""
        return self._logs.copy()

    def clear(self):
        """Menghapus semua log."""
        self._logs.clear()
 
               
class BinaryConverter:
    def __init__(self):
        pass

    def code_to_binary(self, code_str):
        """
        Mengonversi string kode Python ke biner (ASCII).
        """
        binary = ' '.join(format(ord(c), '08b') for c in code_str)
        return binary

    def file_to_binary(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return self.code_to_binary(content)

    def binary_to_code(self, binary_str):
        """
        Mengonversi biner ASCII ke string Python.
        """
        chars = binary_str.split()
        try:
            return ''.join([chr(int(b, 2)) for b in chars])
        except Exception as e:
            return f"❌ Error dalam mengonversi biner: {e}"


# === Pemakaian global (jika ingin akses dari luar) ===
tracker = CodeTracker()
binary_tool = BinaryConverter()


# === Contoh fungsi pengguna yang dipantau ===
@tracker.log_function_call
def contoh_fungsi(a, b):
    return a + b
  
      
class ByteConverter:
    SUFFIXES = ["B", "KB", "MB", "GB", "TB", "PB"]

    @classmethod
    def convert(cls, size_bytes, precision=2):
        """
        Mengubah ukuran byte menjadi string yang terbaca (KB, MB, dst.)
        :param size_bytes: int atau float, ukuran dalam byte
        :param precision: int, jumlah angka desimal
        :return: str
        """
        if size_bytes < 0:
            raise ValueError("Ukuran byte tidak boleh negatif.")
        idx = 0
        while size_bytes >= 1024 and idx < len(cls.SUFFIXES) - 1:
            size_bytes /= 1024.0
            idx += 1
        return f"{size_bytes:.{precision}f} {cls.SUFFIXES[idx]}"

    @classmethod
    def to_bytes(cls, value, unit):
        """
        Mengubah nilai dari unit tertentu (KB, MB, ...) ke byte.
        """
        unit = unit.upper()
        if unit not in cls.SUFFIXES:
            raise ValueError(f"Unit tidak dikenal: {unit}")
        idx = cls.SUFFIXES.index(unit)
        return int(value * (1024 ** idx))

# Tandai bahwa DAFE hanya internal
builtins.__dafe_protect__ = getattr(builtins, "__dafe_protect__", False)
if not builtins.__dafe_protect__:
    # Jika user coba import DAFE langsung, lempar error
    raise ImportError("❌ DAFE tidak boleh diakses langsung.")

# logger khusus (tidak menulis ke console secara default)
logger = logging.getLogger("dearning.dafe")
logger.setLevel(logging.INFO)
# handler default menulis ke file tersembunyi di home directory
HOME = Path.home()
DAFE_DIR = HOME / ".dearning"
DAFE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = DAFE_DIR / "dafe.log"
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
# jangan tambahkan StreamHandler agar tidak muncul di console
logger.addHandler(file_handler)

class DafeGuard:
    def __init__(self, window_size=500, anomaly_threshold=8.0, telemetry_opt_in=False, auto_instrument=False):
        self.logs = []
        self.errors = []
        self.window_size = int(window_size)
        self.anomaly_threshold = float(anomaly_threshold)
        self.telemetry_opt_in = bool(telemetry_opt_in)
        self.auto_instrument = bool(auto_instrument)

        # queue & statistik
        self._queue = deque(maxlen=self.window_size)
        self._mean = None
        self._cov = None
        self._cov_inv = None
        self._lock = threading.RLock()
        self._stop_event = threading.Event()

        # metadata
        self._meta = {
            "created_at": time.time(),
            "python_version": sys.version,
            "dearning_version": self._detect_package_version()
        }

        # === Quantum Engine ===
        try:
            self.quantum = Quantum(qubit_size=4)
            self.use_quantum = True
            logger.info("[DAFE] Quantum engine initialized.")
        except Exception:
            self.quantum = None
            self.use_quantum = False
            logger.warning("[DAFE] Quantum engine unavailable, fallback to classical mode.")

        # scan & start background
        self.scan_environment()
        self._bg_thread = threading.Thread(target=self._background_worker, daemon=True)
        self._bg_thread.start()
        if self.auto_instrument:
            logger.info("[DAFE] Auto-instrumentation requested (not enabled by default).")

        # initial checks (silent)
        self.scan_environment()

        # start background worker
        self._bg_thread = threading.Thread(target=self._background_worker, daemon=True)
        self._bg_thread.start()

        # if auto_instrument True, you can implement function wrappers (dangerous) — TODO
        if self.auto_instrument:
            logger.info("[DAFE] Auto-instrumentation requested (not enabled by default).")

    # -----------------------
    # Environment checks
    # -----------------------
    def _detect_package_version(self):
        try:
            # try to read package version from package metadata if present
            import importlib.metadata as imd
            return imd.version("dearning")
        except Exception:
            return "unknown"

    def scan_environment(self):
        try:
            base_path = os.path.dirname(__file__)
            total_size = self.get_directory_size(base_path)
            self.logs.append(f"[DAFE] 📦 Ukuran total dearning: {total_size / 1024:.2f} KB")
            if sys.version_info < (3, 11):
                self.errors.append("❗ Python < 3.11 tidak didukung oleh dearning.")
            # log silently
            for l in self.logs:
                logger.info(l)
            for e in self.errors:
                logger.warning(e)
        except Exception as e:
            self.errors.append(f"[DAFE] Internal error: {str(e)}")
            logger.exception("DAFE scan_environment error")

    def get_directory_size(self, path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
        return total

    # -----------------------
    # record_event + quantum
    # -----------------------
    def record_event(self, feature_vector, meta=None):
        if np is None:
            logger.info("[DAFE] record_event (numpy not installed) meta=%s", str(meta))
            return

        x = np.asarray(feature_vector, dtype=float).flatten()

        # --- Transformasi Quantum ---
        if self.use_quantum:
            try:
                # contoh: map vektor ke amplitudo qubit dan lakukan Hadamard
                # skala sederhana: ambil max 4 dimensi pertama
                qvec = x[:self.quantum.qubit_size]
                # normalisasi ke [0,1]
                qvec_norm = qvec / (np.max(np.abs(qvec)) + 1e-8)
                # set state amplitudes
                for idx, amp in enumerate(qvec_norm):
                    self.quantum.state[idx] = complex(amp, 0)
                    self.quantum.hadamard_gate(idx)  # Hadamard gate -> superposisi
                # measurement (return probabilitas)
                q_measure = self.quantum.measure()
                # ubah kembali ke vektor numerik
                x[:self.quantum.qubit_size] = np.array([float(b) for b in q_measure["result"]])
            except Exception:
                logger.debug("[DAFE] Quantum transform failed, fallback classical.")
        
        # --- Queue & Mahalanobis ---
        with self._lock:
            self._queue.append(x)
            if len(self._queue) >= 2:
                self._update_stats()

            score = self._mahalanobis_distance(x) if self._cov_inv is not None else 0.0
            if score > self.anomaly_threshold:
                logger.warning("[DAFE] Suspicious activity detected (score=%.3f) meta=%s", score, str(meta))
                self._store_flagged(x, score, meta)
            else:
                logger.debug("[DAFE] event score=%.3f", score)

    def _store_flagged(self, x, score, meta):
        rec = {
            "ts": time.time(),
            "score": float(score),
            "meta": meta or {},
            "vector_mean": self._mean.tolist() if self._mean is not None else None
        }
        # append to a local audit log file
        audit_file = DAFE_DIR / "audit.jsonl"
        try:
            with open(audit_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
        except Exception:
            logger.exception("DAFE failed to write audit record")

    # -----------------------
    # Math: mean & covariance (matrix) + Mahalanobis
    # -----------------------
    def _update_stats(self):
        """Compute mean and covariance from current window (simple batch recompute)."""
        arr = np.vstack(self._queue)   # shape (n, d)
        self._mean = np.mean(arr, axis=0)
        # regularized covariance
        cov = np.cov(arr, rowvar=False)
        # regularize to avoid singular matrix
        eps = 1e-6
        cov += np.eye(cov.shape[0]) * eps
        self._cov = cov
        try:
            self._cov_inv = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            self._cov_inv = None
            logger.debug("DAFE covariance inversion failed (singular matrix)")

    def _mahalanobis_distance(self, x):
        if self._mean is None or self._cov_inv is None:
            return 0.0
        delta = x - self._mean
        m = float(delta.T.dot(self._cov_inv).dot(delta))
        return m  # higher = more anomalous

    # -----------------------
    # Background worker: periodic maintenance & optional updates
    # -----------------------
    def _background_worker(self):
        logger.info("[DAFE] Background worker started.")
        while not self._stop_event.is_set():
            try:
                # periodic maintenance every N seconds
                time.sleep(5)

                # do lightweight self-checks
                if len(self._queue) and (time.time() % 60) < 5:
                    # try re-evaluate cov inverse in case it becomes stable
                    with self._lock:
                        if self._queue:
                            self._update_stats()

                # optional telemetry uploader (only if user opted in)
                if self.telemetry_opt_in:
                    # prepare small anonymous summary (counts, mean norms, flagged count)
                    try:
                        self._upload_telemetry_summary()
                    except Exception:
                        logger.debug("DAFE telemetry upload failed (ignored)")
            except Exception:
                logger.exception("DAFE background_worker error (ignored)")

        logger.info("[DAFE] Background worker stopped.")

    def _upload_telemetry_summary(self):
        """
        Telemetry uploader placeholder.
        Must be enabled only when user explicitly opt-in and with clear consent.
        Here we just write telemetry to a local file as placeholder.
        """
        summary = {
            "ts": time.time(),
            "queue_len": len(self._queue),
            "mean_norm": float(0 if self._mean is None else np.linalg.norm(self._mean)),
            "dearning_version": self._meta.get("dearning_version")
        }
        tfile = DAFE_DIR / "telemetry_summary.jsonl"
        with open(tfile, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(summary) + "\n")

    # -----------------------
    # Shutdown & helpers
    # -----------------------
    def stop(self):
        self._stop_event.set()
        if self._bg_thread.is_alive():
            self._bg_thread.join(timeout=1.0)

    def report(self):
        """
        Human-readable report (written to hidden log file).
        If user wants to see it, provide a CLI command to print it explicitly.
        """
        logger.info("DAFE report requested.")
        # minimal console-safe output if environment variable set
        if os.environ.get("DAFE_VERBOSE") == "1":
            for e in self.errors:
                print("[DAFE] ERROR:", e)
            for l in self.logs:
                print("[DAFE]", l)

# create a global instance so it runs automatically on import within package
_global_dafe = DafeGuard()
record_event = _global_dafe.record_event
