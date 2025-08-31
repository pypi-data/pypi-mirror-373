import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.preprocessing import StandardScaler
from joblib import Parallel, delayed
import logging

logging.basicConfig(level=logging.INFO)
_scaler = StandardScaler()

# === 🔧 Preprocessing Otomatis ===
def preprocess_data(data, n_jobs=-1):
    if isinstance(data, list):
        data = np.array(data)
    if data.shape[0] > 1000:
        batch_size = 200
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        scaled_batches = Parallel(n_jobs=n_jobs)(
            delayed(_scaler.fit_transform)(batch) for batch in batches
        )
        return np.vstack(scaled_batches)
    else:
        return _scaler.fit_transform(data)

# === 🧠 Evaluasi Otomatis (Regresi/Klasifikasi) ===
def evaluate_model(model, data, labels=None, task=None, threshold=0.5):
    y_pred = model.forward(data)

    # Tentukan jenis tugas jika tidak diberikan
    if task is None:
        task = "classification" if set(np.unique(labels).flatten()) <= {0, 1} else "regression"
        logging.info(f"[Auto Task Detection] Deteksi tugas: {task}")
    result = {}
    if labels is None:
        return {"output_mean": float(np.mean(y_pred))}
    if task == "regression":
        result["mse"] = float(mean_squared_error(labels, y_pred))
        result["r2"] = float(r2_score(labels, y_pred))
        result["mean_error"] = float(np.mean(np.abs(y_pred - labels)))
    elif task == "classification":
        y_class = (y_pred > threshold).astype(int)
        result["accuracy"] = float(accuracy_score(labels, y_class))
        result["precision"] = float(precision_score(labels, y_class, zero_division=0))
        result["recall"] = float(recall_score(labels, y_class, zero_division=0))
        result["f1_score"] = float(f1_score(labels, y_class, zero_division=0))
        result["confusion_matrix"] = confusion_matrix(labels, y_class).tolist()
        result["report"] = classification_report(labels, y_class, output_dict=True)
    else:
        raise ValueError("task harus 'regression' atau 'classification'")
    return result
 
# optimizer canggih   
class Optimizer:
    def __init__(self, method="sgd", learning_rate=0.01, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.method = method.lower()
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m_w, self.v_w = {}, {}
        self.m_b, self.v_b = {}, {}
        self.t = 1

    def update(self, w, b, grad_w, grad_b, layer_idx):
        if self.method == "sgd":
            return w - self.lr * grad_w, b - self.lr * grad_b
        elif self.method == "momentum":
            if layer_idx not in self.m_w:
                self.m_w[layer_idx] = np.zeros_like(grad_w)
                self.m_b[layer_idx] = np.zeros_like(grad_b)
            self.m_w[layer_idx] = self.beta1 * self.m_w[layer_idx] + (1 - self.beta1) * grad_w
            self.m_b[layer_idx] = self.beta1 * self.m_b[layer_idx] + (1 - self.beta1) * grad_b
            return w - self.lr * self.m_w[layer_idx], b - self.lr * self.m_b[layer_idx]
        elif self.method == "rmsprop":
            if layer_idx not in self.v_w:
                self.v_w[layer_idx] = np.zeros_like(grad_w)
                self.v_b[layer_idx] = np.zeros_like(grad_b)
            self.v_w[layer_idx] = self.beta2 * self.v_w[layer_idx] + (1 - self.beta2) * grad_w**2
            self.v_b[layer_idx] = self.beta2 * self.v_b[layer_idx] + (1 - self.beta2) * grad_b**2
            return (w - self.lr * grad_w / (np.sqrt(self.v_w[layer_idx]) + self.epsilon),
                    b - self.lr * grad_b / (np.sqrt(self.v_b[layer_idx]) + self.epsilon))
        elif self.method == "adam":
            if layer_idx not in self.m_w:
                self.m_w[layer_idx] = np.zeros_like(grad_w)
                self.v_w[layer_idx] = np.zeros_like(grad_w)
                self.m_b[layer_idx] = np.zeros_like(grad_b)
                self.v_b[layer_idx] = np.zeros_like(grad_b)
            self.m_w[layer_idx] = self.beta1 * self.m_w[layer_idx] + (1 - self.beta1) * grad_w
            self.v_w[layer_idx] = self.beta2 * self.v_w[layer_idx] + (1 - self.beta2) * grad_w**2
            self.m_b[layer_idx] = self.beta1 * self.m_b[layer_idx] + (1 - self.beta1) * grad_b
            self.v_b[layer_idx] = self.beta2 * self.v_b[layer_idx] + (1 - self.beta2) * grad_b**2
            m_w_hat = self.m_w[layer_idx] / (1 - self.beta1 ** self.t)
            v_w_hat = self.v_w[layer_idx] / (1 - self.beta2 ** self.t)
            m_b_hat = self.m_b[layer_idx] / (1 - self.beta1 ** self.t)
            v_b_hat = self.v_b[layer_idx] / (1 - self.beta2 ** self.t)

            self.t += 1
            w_update = self.lr * m_w_hat / (np.sqrt(v_w_hat) + self.epsilon)
            b_update = self.lr * m_b_hat / (np.sqrt(v_b_hat) + self.epsilon)
            return w - w_update, b - b_update
        else:
            raise ValueError(f"Optimizer '{self.method}' tidak dikenali.")