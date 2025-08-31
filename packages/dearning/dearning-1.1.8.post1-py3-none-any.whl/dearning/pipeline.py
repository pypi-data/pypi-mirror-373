import numpy as np
from dearning.model import CustomAIModel, Dense, Activation, DOtensor
from dearning.training import train
from dearning.utils import evaluate_model
from dearning.AI_tools import RLTools
from dearning import (
    TextToSpeech,
    CodeTracker, BinaryConverter
)

def build_basic_model():
    model = CustomAIModel(loss="cross_entropy")
    model.add(Dense(7, 16))
    model.add(Activation("relu"))
    model.add(Dense(16, 8))
    model.add(Activation("tanh"))
    model.add(Dense(8, 4))
    model.add(Activation("softmax"))
    return model

def full_pipeline(task="classification"):
    print("🚀 Menjalankan pipeline dearning...")
    model = build_basic_model()
    model, evaluation = train(model=model, task=task)
    print("🎯 Evaluasi Model:", evaluation)

def rl_pipeline():
    print("🧠 Menjalankan Reinforcement Learning pipeline...")
    rl = RLTools()
    rl.add_q_agent()
    rl.add_random_agent()
    rl.run(episodes=50)
    
def run_pipeline(task="tts", input_data=None):
    if task == "tts":
        TextToSpeech(input_data)
    elif task == "track":
        CodeTracker().track(input_data)
    elif task == "binary":
        bincode = BinaryConverter().convert_file(input_data)
        print("Hasil Biner:", bincode)
    
def train_model(model, task="classification", X=None, y=None, 
                epochs=100, learning_rate=0.01, batch_size=32, 
                visualize=True, use_autograd=False, use_dotensor=False, trace=False):
    """
    Pipeline standar untuk pelatihan model.
    """
    if X is None or y is None:
        X = np.random.rand(300, 4)
        y = np.random.randint(0, 2, size=(300, 1) if task == "classification" else (300,))

    if use_dotensor:
        X_tensor = [DOtensor(x, requires_grad=True) for x in X]
        y_tensor = [DOtensor(y_val) for y_val in y]
        
        for epoch in range(epochs):
            total_loss = 0
            for x_t, y_t in zip(X_tensor, y_tensor):
                out = model.forward(x_t.data.reshape(1, -1))
                pred = DOtensor(out[0])
                target = y_t
                loss = (pred - target) * (pred - target)

                if trace:
                    print(f"🧠 Loss graph: {loss}")

                loss.backward()
                total_loss += float(loss.data)

            avg_loss = total_loss / len(X_tensor)
            print(f"[DOtensor] Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")

        return model, {"loss": avg_loss}
    
    else:
        model.train(X, y, epochs=epochs, learning_rate=learning_rate, batch_size=batch_size, verbose=visualize)
        return model, {"loss": model.losses[-1] if model.losses else None}
    
def run_ai(model_name, task_input):
    return
