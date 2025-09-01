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
def preprocess_data(data, n_jobs=-1, optimizer_args=None):
    if isinstance(data, list):
        data = np.array(data)
    if data.shape[0] > 1000:
        batch_size = 200
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        scaled_batches = Parallel(n_jobs=n_jobs)(
            delayed(_scaler.fit_transform)(batch) for batch in batches
        )
        data_scaled = np.vstack(scaled_batches)
    else:
        data_scaled = _scaler.fit_transform(data)
    # Optimizer logic (if optimizer_args provided)
    if optimizer_args is not None:
        w, b, grad_w, grad_b, layer_idx = optimizer_args[:5]
        method = optimizer_args[5] if len(optimizer_args) > 5 else "sgd"
        learning_rate = optimizer_args[6] if len(optimizer_args) > 6 else 0.01
        beta1 = optimizer_args[7] if len(optimizer_args) > 7 else 0.9
        beta2 = optimizer_args[8] if len(optimizer_args) > 8 else 0.999
        epsilon = optimizer_args[9] if len(optimizer_args) > 9 else 1e-8
        state = optimizer_args[10] if len(optimizer_args) > 10 else {}
        method = method.lower()
        if method == "sgd":
            w_new = w - learning_rate * grad_w
            b_new = b - learning_rate * grad_b
        elif method == "momentum":
            m_w = state.get("m_w", {})
            m_b = state.get("m_b", {})
            if layer_idx not in m_w:
                m_w[layer_idx] = np.zeros_like(grad_w)
                m_b[layer_idx] = np.zeros_like(grad_b)
            m_w[layer_idx] = beta1 * m_w[layer_idx] + (1 - beta1) * grad_w
            m_b[layer_idx] = beta1 * m_b[layer_idx] + (1 - beta1) * grad_b
            state["m_w"], state["m_b"] = m_w, m_b
            w_new = w - learning_rate * m_w[layer_idx]
            b_new = b - learning_rate * m_b[layer_idx]
        elif method == "rmsprop":
            v_w = state.get("v_w", {})
            v_b = state.get("v_b", {})
            if layer_idx not in v_w:
                v_w[layer_idx] = np.zeros_like(grad_w)
                v_b[layer_idx] = np.zeros_like(grad_b)
            v_w[layer_idx] = beta2 * v_w[layer_idx] + (1 - beta2) * grad_w**2
            v_b[layer_idx] = beta2 * v_b[layer_idx] + (1 - beta2) * grad_b**2
            state["v_w"], state["v_b"] = v_w, v_b
            w_new = w - learning_rate * grad_w / (np.sqrt(v_w[layer_idx]) + epsilon)
            b_new = b - learning_rate * grad_b / (np.sqrt(v_b[layer_idx]) + epsilon)
        elif method == "adam":
            m_w = state.get("m_w", {})
            v_w = state.get("v_w", {})
            m_b = state.get("m_b", {})
            v_b = state.get("v_b", {})
            t = state.get("t", 1)
            if layer_idx not in m_w:
                m_w[layer_idx] = np.zeros_like(grad_w)
                v_w[layer_idx] = np.zeros_like(grad_w)
                m_b[layer_idx] = np.zeros_like(grad_b)
                v_b[layer_idx] = np.zeros_like(grad_b)
            m_w[layer_idx] = beta1 * m_w[layer_idx] + (1 - beta1) * grad_w
            v_w[layer_idx] = beta2 * v_w[layer_idx] + (1 - beta2) * grad_w**2
            m_b[layer_idx] = beta1 * m_b[layer_idx] + (1 - beta1) * grad_b
            v_b[layer_idx] = beta2 * v_b[layer_idx] + (1 - beta2) * grad_b**2
            m_w_hat = m_w[layer_idx] / (1 - beta1 ** t)
            v_w_hat = v_w[layer_idx] / (1 - beta2 ** t)
            m_b_hat = m_b[layer_idx] / (1 - beta1 ** t)
            v_b_hat = v_b[layer_idx] / (1 - beta2 ** t)
            t += 1
            state.update({"m_w": m_w, "v_w": v_w, "m_b": m_b, "v_b": v_b, "t": t})
            w_update = learning_rate * m_w_hat / (np.sqrt(v_w_hat) + epsilon)
            b_update = learning_rate * m_b_hat / (np.sqrt(v_b_hat) + epsilon)
            w_new = w - w_update
            b_new = b - b_update
        else:
            raise ValueError(f"Optimizer '{method}' tidak dikenali.")
        return data_scaled, (w_new, b_new, state)
    return data_scaled

def evaluate_model(model, data, labels=None, task=None, threshold=0.5, optimizer_args=None):
    y_pred = model.forward(data)
    # Optimizer logic (if optimizer_args provided)
    if optimizer_args is not None:
        w, b, grad_w, grad_b, layer_idx = optimizer_args[:5]
        method = optimizer_args[5] if len(optimizer_args) > 5 else "sgd"
        learning_rate = optimizer_args[6] if len(optimizer_args) > 6 else 0.01
        beta1 = optimizer_args[7] if len(optimizer_args) > 7 else 0.9
        beta2 = optimizer_args[8] if len(optimizer_args) > 8 else 0.999
        epsilon = optimizer_args[9] if len(optimizer_args) > 9 else 1e-8
        state = optimizer_args[10] if len(optimizer_args) > 10 else {}
        method = method.lower()
        if method == "sgd":
            w_new = w - learning_rate * grad_w
            b_new = b - learning_rate * grad_b
        elif method == "momentum":
            m_w = state.get("m_w", {})
            m_b = state.get("m_b", {})
            if layer_idx not in m_w:
                m_w[layer_idx] = np.zeros_like(grad_w)
                m_b[layer_idx] = np.zeros_like(grad_b)
            m_w[layer_idx] = beta1 * m_w[layer_idx] + (1 - beta1) * grad_w
            m_b[layer_idx] = beta1 * m_b[layer_idx] + (1 - beta1) * grad_b
            state["m_w"], state["m_b"] = m_w, m_b
            w_new = w - learning_rate * m_w[layer_idx]
            b_new = b - learning_rate * m_b[layer_idx]
        elif method == "rmsprop":
            v_w = state.get("v_w", {})
            v_b = state.get("v_b", {})
            if layer_idx not in v_w:
                v_w[layer_idx] = np.zeros_like(grad_w)
                v_b[layer_idx] = np.zeros_like(grad_b)
            v_w[layer_idx] = beta2 * v_w[layer_idx] + (1 - beta2) * grad_w**2
            v_b[layer_idx] = beta2 * v_b[layer_idx] + (1 - beta2) * grad_b**2
            state["v_w"], state["v_b"] = v_w, v_b
            w_new = w - learning_rate * grad_w / (np.sqrt(v_w[layer_idx]) + epsilon)
            b_new = b - learning_rate * grad_b / (np.sqrt(v_b[layer_idx]) + epsilon)
        elif method == "adam":
            m_w = state.get("m_w", {})
            v_w = state.get("v_w", {})
            m_b = state.get("m_b", {})
            v_b = state.get("v_b", {})
            t = state.get("t", 1)
            if layer_idx not in m_w:
                m_w[layer_idx] = np.zeros_like(grad_w)
                v_w[layer_idx] = np.zeros_like(grad_w)
                m_b[layer_idx] = np.zeros_like(grad_b)
                v_b[layer_idx] = np.zeros_like(grad_b)
            m_w[layer_idx] = beta1 * m_w[layer_idx] + (1 - beta1) * grad_w
            v_w[layer_idx] = beta2 * v_w[layer_idx] + (1 - beta2) * grad_w**2
            m_b[layer_idx] = beta1 * m_b[layer_idx] + (1 - beta1) * grad_b
            v_b[layer_idx] = beta2 * v_b[layer_idx] + (1 - beta2) * grad_b**2
            m_w_hat = m_w[layer_idx] / (1 - beta1 ** t)
            v_w_hat = v_w[layer_idx] / (1 - beta2 ** t)
            m_b_hat = m_b[layer_idx] / (1 - beta1 ** t)
            v_b_hat = v_b[layer_idx] / (1 - beta2 ** t)
            t += 1
            state.update({"m_w": m_w, "v_w": v_w, "m_b": m_b, "v_b": v_b, "t": t})
            w_update = learning_rate * m_w_hat / (np.sqrt(v_w_hat) + epsilon)
            b_update = learning_rate * m_b_hat / (np.sqrt(v_b_hat) + epsilon)
            w_new = w - w_update
            b_new = b - b_update
        else:
            raise ValueError(f"Optimizer '{method}' tidak dikenali.")
        optimizer_result = (w_new, b_new, state)
    else:
        optimizer_result = None
    # Tentukan jenis tugas jika tidak diberikan
    if task is None:
        task = "classification" if set(np.unique(labels).flatten()) <= {0, 1} else "regression"
        logging.info(f"[Auto Task Detection] Deteksi tugas: {task}")
    result = {}
    if labels is None:
        result = {"output_mean": float(np.mean(y_pred))}
    elif task == "regression":
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
    if optimizer_result is not None:
        return result, optimizer_result
    return result