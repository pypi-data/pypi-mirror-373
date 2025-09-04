from dearning.model import CustomAIModel
from dearning.utils import preprocess_data, evaluate_model
from dearning import Quantum
import numpy as np
from decimal import Decimal
from fractions import Fraction
from functools import reduce
import matplotlib.pyplot as plt
import threading, time, logging, os, math
from PIL import Image
from sklearn.datasets import make_classification, make_regression

# Autograd (opsional)
try:
    import autograd.numpy as anp
    from autograd import grad
    AUTOGRAD_AVAILABLE = True
except ImportError:
    AUTOGRAD_AVAILABLE = False

# === LOGEKSTRAINNIX ===
class LogEkstrainnix:
    """
    Transformasi input menggunakan:
    - eksponensial, logaritma, matrix, linear universe
    - quantum superposition (Triplogonoras-Quantum-Eksponentrix)
    - kompatibel dengan Autograd jika tersedia
    """
    def __init__(self, use_quantum=True, qubit_size=4):
        self.use_quantum = use_quantum
        self.qubit_size = qubit_size
        if self.use_quantum:
            try:
                self.quantum = Quantum(qubit_size=self.qubit_size)
            except Exception:
                self.quantum = None
                self.use_quantum = False

    def linear_universe(self, X):        
        # komponen linear dan kuadrat
        base = X + X**2 + 0.5*X  
        # komponen aljabar (cross-term antar variabel)
        if X.ndim == 2 and X.shape[1] > 1:
            cross_terms = np.zeros_like(X)
            for i in range(X.shape[1]):
                for j in range(i+1, X.shape[1]):
                    cross_terms[:, i] += X[:, i] * X[:, j]
            base += 0.1 * cross_terms  # skala kecil agar tidak dominan
        return base


    def Qtransform(self, X):
        """Transformasikan X menggunakan Quantum (Hadamard + Measurement)"""
        X_transformed = X.copy()
        for i in range(min(self.qubit_size, X.shape[1])):
            self.quantum.state[i] = complex(X[0, i], 0)  # ambil 1 sample sebagai contoh
            self.quantum.hadamard_gate(i)
        q_meas = self.quantum.measure()
        # hasil measurement -> biner ke float
        X_transformed[:, :self.qubit_size] = np.array(
            [[float(b) for b in q_meas["result"]]] * X.shape[0]
        )
        return X_transformed

    def transform(self, X):
        """Transformasi log + exp + matrix + linear universe + quantum"""
        xp = anp if AUTOGRAD_AVAILABLE else np

        # Hindari log(0)
        X_safe = xp.where(X <= 0, 1e-8, X)
        X_log = xp.log(X_safe)
        X_exp = xp.exp(X)
        # Matrix mix
        if X.ndim == 2:
            mat = xp.dot(X.T, X)
            mat_avg = mat / xp.max(mat) if xp.max(mat) != 0 else mat
            X_matrixed = xp.dot(X, mat_avg)
        else:
            X_matrixed = X

        # Linear universe
        X_linear = self.linear_universe(X_matrixed)
        # Gabungkan semua transformasi
        X_final = (X_log + X_exp + X_linear) / 3.0

        # Quantum transform
        if self.use_quantum:
            try:
                X_final = self.quantum_transform(X_final)
            except Exception:
                pass  # fallback ke classica
        return X_final


# === Data load ===
def load_dataset(task="classification", n_samples=500, n_features=4):
    if task == "classification":
        n_informative = max(2, min(n_features, n_features - 2))
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_informative,
            n_redundant=0,
            n_repeated=0,
            n_classes=2,
            random_state=42
        )
        y = y.reshape(-1, 1)
    elif task == "regression":
        X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=0.1)
        y = y.reshape(-1, 1)
    else:
        raise ValueError("Task harus 'classification' atau 'regression'")
    return X, y

def data_loader(X, y, batch_size=32, shuffle=True):
    n = X.shape[0]
    indices = np.arange(n)
    if shuffle:
        np.random.shuffle(indices)
    for start in range(0, n, batch_size):
        end = start + batch_size
        idx = indices[start:end]
        yield X[idx], y[idx]
        
def load_image_dataset(folder_path, size=(64, 64), label_type="folder"):
    """
    Load gambar dari folder menjadi dataset (X, y)
    label_type: "folder" = nama folder jadi label
    """
    X = []
    y = []
    class_map = {}
    class_idx = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(root, file)
                img = Image.open(path).convert("RGB").resize(size)
                X.append(np.asarray(img) / 255.0)

                if label_type == "folder":
                    label_name = os.path.basename(os.path.dirname(path))
                    if label_name not in class_map:
                        class_map[label_name] = class_idx
                        class_idx += 1
                    y.append(class_map[label_name])

    X = np.array(X)
    y = np.array(y).reshape(-1, 1)
    print(f"📸 Loaded {len(X)} images from {folder_path}")
    return X, y

# === Training dengan Autograd ===
def trainautograd(model, X, y, epochs=100, lr=0.01, verbose=True):
    def loss_fn(weights_flattened):
        weights = weights_flattened.reshape(model.input_size, model.output_size)
        preds = anp.dot(X, weights)
        loss = anp.mean((preds - y) ** 2)
        return loss

    grad_fn = grad(loss_fn)
    weights = model.weights.copy().flatten()
    model.losses = []

    for epoch in range(epochs):
        grad_val = grad_fn(weights)
        weights -= lr * grad_val
        loss = loss_fn(weights)
        model.losses.append(loss)
        if verbose:
            print(f"[AutoGrad] Epoch {epoch+1}/{epochs} - Loss: {loss:.4f}")

    model.weights = weights.reshape(model.input_size, model.output_size)

# === Logging ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# === Evaluasi Komprehensif ===
def fullevaluation(model, X, y, task):
    result = evaluate_model(model, X, y, task)
    logging.info(f"📊 Evaluasi Model: {result}")
    return result

# === Training Utama ===
def train(model, task="classification", visualize=True,
                epochs=100, learning_rate=0.05, batch_size=32,
                use_autograd=False, use_logekstrainnix=False):

    n_features = model.layer_sizes[0]
    X, y = load_dataset(task=task, n_samples=500, n_features=n_features)
    X = preprocess_data(X)

    if use_logekstrainnix:
        logex = LogEkstrainnix()
        X = logex.transform(X)  # Transformasi khusus sebelum training

    def trainingthread():
        logging.info("🔧 Training dimulai...")
        if use_autograd and AUTOGRAD_AVAILABLE and hasattr(model, "weights"):
            trainautograd(model, X, y, epochs=epochs, lr=learning_rate)
        else:
            model.train(X, y, epochs=epochs, learning_rate=learning_rate, batch_size=batch_size)
        logging.info("✅ Training selesai.")

    start = time.time()
    thread = threading.Thread(target=trainingthread)
    thread.start()
    thread.join()
    end = time.time()

    eval_result = fullevaluation(model, X, y, task)

    if visualize:
        try:
            import matplotlib.pyplot as plt
            plt.plot(model.losses)
            plt.title("Grafik Loss selama Training")
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.grid(True)
            plt.show()
        except:
            logging.warning("Gagal visualisasi. Pastikan matplotlib terinstal.")

    print("📌 Waktu training: {:.2f} detik".format(end - start))
    print("🎯 Hasil evaluasi:", eval_result)
    return model, eval_result

# === Multi Model Training (opsional) ===
def trainmultipel(n=3, input_size=4, output_size=1, task="classification",
                  use_autograd=False, use_logekstrainnix=False):
    """
    Training beberapa model sekaligus dengan dukungan logekstrainnix dan linear universe.
    """
    models = []
    for i in range(n):
        print(f"🚀 Training model-{i+1}/{n}")
        model = CustomAIModel(
            layer_sizes=[input_size, 16, 8, output_size],
            activations=["memory", "attention", "spiking"],  # contoh kombinasi yang ada
            loss="mse" if task == "regression" else "cross_entropy"
        )

        # Jalankan training per model
        train(model, task=task, use_autograd=use_autograd, use_logekstrainnix=use_logekstrainnix)
        models.append(model)
    return models


# === Eksekusi Utama ===
if __name__ == "__main__":
    model = CustomAIModel(
        layer_sizes=[4, 16, 8, 1],
        activations=["memory", "attention", "spiking"],  # pakai yang ada
        loss="cross_entropy"
    )
    train(model, task="classification", use_autograd=False)