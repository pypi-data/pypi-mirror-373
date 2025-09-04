from PIL import Image
import io, os, ast, struct, pyttsx3, wave, logging, contextlib, scipy.signal as signal, subprocess, sys, platform, numpy as np
from scipy.signal import resample
from scipy.fftpack import dct
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
# === Ekstrak Libraries ===
def ekstractlibraries():
    try:
        import networkx as nx
        NETWORKX_AVAILABLE = True
    except ImportError:
        NETWORKX_AVAILABLE = False
    try:
        from geopy.geocoders import Nominatim
        GEOPY_AVAILABLE = True
    except ImportError:
        GEOPY_AVAILABLE = False
    try:
        import serial
        PYSERIAL_AVAILABLE = True
    except ImportError:
        PYSERIAL_AVAILABLE = False

# === NLP: Analisis ===
class DLP:
    def __init__(self, lang="en"):
        self.lang = lang

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity,
            "label": "positive" if blob.sentiment.polarity > 0
                     else "negative" if blob.sentiment.polarity < 0
                     else "neutral"
        }

    def extract_nouns(self, text):
        blob = TextBlob(text)
        return list(blob.noun_phrases)

    def pos_tagging(self, text):
        blob = TextBlob(text)
        return blob.tags

    def summarize(self, text, max_sentences=2):
        sentences = text.split(". ")
        return ". ".join(sentences[:max_sentences]) + ("." if len(sentences) > max_sentences else "")

    def process(self, text):
        result = {
            "sentiment": self.analyze_sentiment(text),
            "nouns": self.extract_nouns(text),
            "pos_tags": self.pos_tagging(text),
            "summary": self.summarize(text)
        }
        return result

# === RL Tools ===
try:
    from simple_rl.agents import QLearningAgent, RandomAgent
    from simple_rl.tasks import GridWorldMDP
    from simple_rl.run_experiments import run_agents_on_mdp

    class RLTools:
        def __init__(self):
            self.env = GridWorldMDP()
            self.agents = []

        def add_q_agent(self, name="q_agent", alpha=0.1, epsilon=0.1, gamma=0.9):
            agent = QLearningAgent(name=name, actions=self.env.get_actions(),
                                   alpha=alpha, epsilon=epsilon, gamma=gamma)
            self.agents.append(agent)
            return agent

        def add_random_agent(self, name="random"):
            agent = RandomAgent(name=name, actions=self.env.get_actions())
            self.agents.append(agent)
            return agent

        def run(self, episodes=100):
            if self.agents:
                run_agents_on_mdp(self.agents, self.env, instances=1, episodes=episodes)
            else:
                print("[⚠️] Tidak ada agen RL yang ditambahkan.")
except ImportError:
    class RLTools:
        def __init__(self):
            print("[❌] simple_rl belum terpasang. Gunakan: pip install simple_rl")
        def add_q_agent(self, *args, **kwargs): pass
        def add_random_agent(self, *args, **kwargs): pass
        def run(self, *args, **kwargs): pass

# === TEXT TO SPEECH ===
class TTS:
    def __init__(self, voice=None, rate=150, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        if voice:
            self.set_voice(voice)

    def set_voice(self, voice_name):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice_name.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

# === MEMORY MANAGEMENT ===
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "Memory", "DATAI.py")
MEMORY_VAR = "memory"

class AImemory:
    def __init__(self):
        self.memory = self._load_memory()

    def _load_memory(self):
        if not os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "w") as f:
                f.write(f"{MEMORY_VAR} = []\n")
            return []

        with open(MEMORY_PATH, "r") as f:
            try:
                content = f.read()
                parsed = ast.parse(content, mode='exec')
                for node in parsed.body:
                    if isinstance(node, ast.Assign) and node.targets[0].id == MEMORY_VAR:
                        return ast.literal_eval(ast.unparse(node.value))
            except Exception as e:
                print("❌ Gagal baca memori:", e)
        return []

    def _save_memory(self):
        with open(MEMORY_PATH, "w") as f:
            f.write(f"{MEMORY_VAR} = {repr(self.memory)}\n")

    def add(self, data):
        if data not in self.memory:
            self.memory.append(data)
            self._save_memory()

    def remove(self, data):
        if data in self.memory:
            self.memory.remove(data)
            self._save_memory()

    def clear(self):
        self.memory = []
        self._save_memory()

    def get_all(self):
        return self.memory

    def contains(self, query):
        return query in self.memory

# === Gambar ===
class image:
    @staticmethod
    def load_image(path, target_size=(64, 64), grayscale=False):
        mode = "L" if grayscale else "RGB"
        img = Image.open(path).convert(mode).resize(target_size)
        arr = np.asarray(img).astype(np.float32)
        arr -= arr.min()
        if arr.max() > 0:
            arr /= arr.max()
        arr = np.clip(arr, 0.0, 1.0)
        return arr

    @staticmethod
    def flatten_image(img_array):
        return img_array.flatten()

# === Audio (DOaudio) ===
class DOaudio:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.channels = 1
        self.sample_width = 2  # bytes (16-bit PCM)
        print(f"[DOaudio] Initialized at {self.sample_rate}Hz")

    # --- Audio Generator ---
    def generate_audio(self, freq=440, duration=1.0, amplitude=0.5):
        """Generate a sine wave audio signal"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        wave_data = amplitude * np.sin(2 * np.pi * freq * t)
        wave_data = np.int16(wave_data * 32767)  # Convert to 16-bit PCM
        return wave_data

    # --- Audio Filter (scipy) ---
    def filter_audio(self, audio_data, cutoff=1000):
        """Apply a low-pass filter to the audio data"""
        b, a = signal.butter(6, cutoff / (0.5 * self.sample_rate), btype='low')
        filtered = signal.lfilter(b, a, audio_data)
        return np.int16(filtered)

    # --- Save to WAV ---
    def save_audio(self, filename, audio_data):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sample_width)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        print(f"[DOaudio] Saved audio to {filename}")

    # --- Play with system tools ---
    def play_audio(self, filename):
        """Play audio using OS tools (depends on platform)"""
        system_name = platform.system()
        try:
            if system_name == "Windows":
                os.startfile(filename)
            elif system_name == "Darwin":  # macOS
                subprocess.run(["afplay", filename])
            elif system_name == "Linux" or "Android" in system_name:
                subprocess.run(["aplay", filename])
            else:
                print("[DOaudio] Unsupported system for playback")
        except Exception as e:
            print(f"[DOaudio] Error playing audio: {e}")

# === Video (GIF Frames) ===
class video:
    @staticmethod
    def extract_gif(path, max_frames=10):
        img = Image.open(path)
        frames = []
        try:
            for i in range(max_frames):
                img.seek(i)
                frame = img.convert("RGB")
                arr = np.array(frame).astype(np.float32)
                arr -= arr.mean()
                std = arr.std() + 1e-5
                arr /= std
                arr = np.clip((arr + 0.5), 0.0, 1.0)
                frames.append(arr)
        except EOFError:
            pass
        return np.array(frames)

# === Pemahaman cepat (analisis ringan) ===
class Qkanalyze:
    def top_kprobs(preds, k=3):
        sorted_idx = np.argsort(preds)[::-1]
        top_k = [(int(i), float(preds[i])) for i in sorted_idx[:k]]
        return top_k

    def summarize_array(arr):
        return {
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "shape": arr.shape
        }
