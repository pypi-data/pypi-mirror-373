import numpy as np
from PIL import Image
import io, os, ast, struct, pyttsx3, wave, logging, contextlib
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

# === Audio ===
class audio:
    @staticmethod
    def load_audio(path, sr=22050):
        with wave.open(path, 'rb') as wf:
            sample_rate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_bytes = wf.readframes(n_frames)
            audio = np.frombuffer(audio_bytes, dtype=np.int16)
        if sample_rate != sr:
            audio = resample(audio, int(len(audio) * sr / sample_rate))
            sample_rate = sr
        return audio, sample_rate

    @staticmethod
    def extract_mfcc(path, n_mfcc=13, sr=22050, nfilt=26, nfft=512):
        audio_data, sample_rate = audio.load_audio(path, sr)
        emphasized = np.append(audio_data[0], audio_data[1:] - 0.97 * audio_data[:-1])
        frame_size = 0.025
        frame_stride = 0.01
        frame_length = int(round(frame_size * sample_rate))
        frame_step = int(round(frame_stride * sample_rate))
        signal_length = len(emphasized)
        num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step))
        pad_signal_length = num_frames * frame_step + frame_length
        z = np.zeros((pad_signal_length - signal_length))
        pad_signal = np.append(emphasized, z)
        indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
                  np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
        frames = pad_signal[indices.astype(np.int32, copy=False)]
        frames *= np.hamming(frame_length)
        NFFT = nfft
        mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
        pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))
        low_freq_mel = 0
        high_freq_mel = (2595 * np.log10(1 + (sample_rate / 2) / 700))
        mel_points = np.linspace(low_freq_mel, high_freq_mel, nfilt + 2)
        hz_points = (700 * (10**(mel_points / 2595) - 1))
        bin = np.floor((NFFT + 1) * hz_points / sample_rate)
        fbank = np.zeros((nfilt, int(np.floor(NFFT / 2 + 1))))
        for m in range(1, nfilt + 1):
            f_m_minus = int(bin[m - 1])
            f_m = int(bin[m])
            f_m_plus = int(bin[m + 1])
            for k in range(f_m_minus, f_m):
                fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
            for k in range(f_m, f_m_plus):
                fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])
        filter_banks = np.dot(pow_frames, fbank.T)
        filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
        filter_banks = 20 * np.log10(filter_banks)
        mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, :n_mfcc]
        return mfcc

    @staticmethod
    def get_audio_duration(path):
        with wave.open(path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
        return duration

# === Video (GIF Frames) ===
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
class Qanalyze:
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
