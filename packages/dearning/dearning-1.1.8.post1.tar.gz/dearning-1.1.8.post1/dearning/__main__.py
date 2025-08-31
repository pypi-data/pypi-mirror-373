import argparse, os, sys, time, webbrowser
import numpy as np
from dearning import (
    CustomAIModel, Dense, Activation,
    train, load_image, flatten_image,
    extract_mfcc, DLP
)
from dearning.multymodel import AImodel
from dearning.pipeline import preprocess_data
import dearning  # untuk mengakses lokasi folder dearning
import glob

def find_tutorial_pdf():
    # Daftar lokasi umum untuk HP dan laptop/PC
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "tutorial_dearning.pdf"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "tutorial_dearning.pdf"),
        os.path.expanduser("~/dearning/tutorial_dearning.pdf"),
        os.path.expanduser("~/Documents/dearning/tutorial_dearning.pdf"),
        "/storage/emulated/0/my_libraries/dearning/dearning/tutorial_dearning.pdf",
        "/sdcard/dearning/tutorial_dearning.pdf",
        "tutorial_dearning.pdf"
    ]
    # Cari juga di subfolder dearning
    possible_paths += glob.glob(os.path.join(os.path.dirname(__file__), "**", "tutorial_dearning.pdf"), recursive=True)
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# Tangani --help secara manual (buka PDF jika tersedia)
if "--help" in sys.argv or "--tutorial" in sys.argv:
    pdf_path = find_tutorial_pdf()
    if pdf_path:
        print("📖 Membuka dokumentasi PDF...")
        webbrowser.open(f"file://{os.path.abspath(pdf_path)}")
    else:
        print("❌ File dokumentasi tidak ditemukan di lokasi umum.")
    sys.exit()

def build_default_model(task="classification"):
    model = CustomAIModel(loss="cross_entropy" if task == "classification" else "mse")
    model.add(Dense(4, 16))
    model.add(Activation("relu"))
    model.add(Dense(16, 8))
    model.add(Activation("tanh"))
    model.add(Dense(8, 1))
    model.add(Activation("sigmoid" if task == "classification" else "linear"))
    return model

def get_folder_size(folder):
    total = 0
    for root, _, files in os.walk(folder):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total / 1024  # dalam KB

def main():
    parser = argparse.ArgumentParser(description="🧠 Dearning CLI Interface")
    parser.add_argument("--task", default="classification", choices=["classification", "regression"])
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--image", help="Path ke gambar input")
    parser.add_argument("--audio", help="Path ke audio input")
    parser.add_argument("--text", help="Teks untuk DLP")
    parser.add_argument("--translate", help="Bahasa tujuan")
    parser.add_argument("--model", help="Nama model dari multymodel", default="simpleAI")
    parser.add_argument("--save", help="Simpan model")
    parser.add_argument("--load", help="Load model dari path")
    parser.add_argument("--autograd", action="store_true")
    parser.add_argument("--no-visual", action="store_true")
    parser.add_argument("--size", action="store_true", help="Tampilkan ukuran libraries dearning")

    args = parser.parse_args()
    aimodel = AImodel()
    dlp = DLP()

    # === Ukuran libraries Dearning ===
    if args.size:
        print("📦 Mengukur ukuran Dearning...")
        path = dearning.__path__[0]
        size_kb = get_folder_size(path)
        status = "✅ Cocok untuk device ringan" if size_kb < 300 else (
                 "⚠️ Lumayan, cek performa jika lambat" if size_kb < 1024 else
                 "❌ Terlalu besar untuk device kecil")
        print(f"Ukuran: {size_kb:.2f} KB\nLokasi: {path}\nStatus: {status}")
        return

    # === NLP / DLP ===
    if args.text:
        print("📄 DLP:", dlp.process(args.text, translate_to=args.translate))
        return

    # === Input Preparation ===
    if args.image:
        x = flatten_image(load_image(args.image)).reshape(1, -1)
        input_mode = "image"
    elif args.audio:
        x = extract_mfcc(args.audio).mean(axis=0).reshape(1, -1)
        input_mode = "audio"
    else:
        x = np.random.rand(300, 4)
        y = np.random.randint(0, 2, size=(300, 1))
        input_mode = "train"

    # === Load or Build Model ===
    if args.load and os.path.exists(args.load + "_config.json"):
        model = CustomAIModel.load_model(args.load)
        print(f"📥 Model dimuat dari: {args.load}")
    elif args.model in aimodel.available_models():
        model = aimodel.get_model(args.model)
        print(f"📦 Gunakan model: {args.model}")
    else:
        model = build_default_model(task=args.task)
        print("🆕 Model default dibangun.")

    # === Training or Prediction ===
    if input_mode == "train":
        model, evaluation = train(
            model, task=args.task,
            epochs=args.epochs,
            learning_rate=args.lr,
            batch_size=32,
            visualize=not args.no_visual,
            use_autograd=args.autograd
        )
        if args.save:
            model.save_model(args.save)
            print("💾 Model disimpan ke:", args.save)
    else:
        pred = model.forward(x)
        print("🔮 Prediksi:", pred)

if __name__ == "__main__":
    main()