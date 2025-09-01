# dearning/testing.py
import numpy as np
from math import log, exp, sqrt
from dearning.utils import evaluate_model

def test_model(model, X, y, formula=None, verbose=True):
    """
    Fungsi testing model AI dengan Alogekstest-Phymetrix
    Rumus formula default menggunakan:
    aljabar + logaritma + eksponensial + Phytagoras + geometri + matrix
    """
    # --- Forward pass model ---
    preds = model.forward(X)

    # --- Terapkan formula Alogekstest-Phymetrix ---
    # Misal: transformasi logaritma + eksponensial
    transformed = preds.copy()
    transformed = np.where(transformed > 0, np.log1p(transformed), transformed)  # log
    transformed = np.exp(transformed)  # eksponensial

    # Multi-dimensional Pythagoras (contoh)
    py_values = np.sqrt(np.sum(transformed**2, axis=1, keepdims=True))

    # Kombinasi akhir: normalisasi ke rentang 0-1
    final_preds = py_values / (np.max(py_values) + 1e-8)

    # Evaluasi dengan fungsi built-in dearning
    result = evaluate_model(model, X, y, task="classification")

    # Tambahkan insight Alogekstest-Phymetrix
    result.update({
        "formula_used": formula or "aljabar+logaritma+eksponensial+phytagoras+geometri+matrix",
        "final_preds": final_preds,
        "insight": {
            "mean_prediction": float(np.mean(final_preds)),
            "max_prediction": float(np.max(final_preds)),
            "min_prediction": float(np.min(final_preds))
        }
    })

    if verbose:
        print("📊 Alogekstest-Phymetrix Evaluation:")
        print(f"Accuracy: {result.get('accuracy', 'N/A')}")
        print(f"Loss: {result.get('loss', 'N/A')}")
        print(f"Mean Prediction: {result['insight']['mean_prediction']:.4f}")

    return result
