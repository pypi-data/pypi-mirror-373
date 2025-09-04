import numpy as np
from dearning.AI_tools import DLP
from dearning.utils import preprocess_data

# Lazy import untuk menghindari circular import
def lazy_import():
    from dearning.model import CustomAIModel, Dense, Activation
    return CustomAIModel, Dense, Activation

class AImodel:
    def __init__(self):
        self.models = {}
        self.CustomAIModel, self.Dense, self.Activation = lazy_import()
        self.load_default_models()
        self.dlp = DLP()

    def load_default_models(self):
        self.models['simpleAI'] = self._build_simple_ai()

    def _build_simple_ai(self):
        model = self.CustomAIModel(loss="mse")
        model.add(self.Dense(10, 32))
        model.add(self.Activation("relu"))
        model.add(self.Dense(32, 16))
        model.add(self.Activation("tanh"))
        model.add(self.Dense(16, 6))  # 6 output class
        model.add(self.Activation("softmax"))
        model.memory = []
        return model

    def get_model(self, name):
        return self.models.get(name)

    def predict(self, model_name, data):
        model = self.get_model(model_name)
        if model:
            data = preprocess_data(data)
            return model.forward(data)
        return None

    def save_model(self, model_name, path):
        model = self.get_model(model_name)
        if model:
            model.save_model(path)

    def load_model(self, model_name, path):
        model = self.CustomAIModel.load_model(path)
        self.models[model_name] = model

    def available_models(self):
        return list(self.models.keys())

    def learn_from_mistake(self, model_name, state, wrong_output_idx):
        model = self.get_model(model_name)
        if model and hasattr(model, "memory"):
            label = np.zeros((6,))
            label[wrong_output_idx] = 0.1
            model.memory.append((state, label))

    def train_from_memory(self, model_name, correct_index):
        model = self.get_model(model_name)
        if model and hasattr(model, "memory") and model.memory:
            data = np.array([m[0] for m in model.memory])
            labels = []
            for m in model.memory:
                lbl = m[1]
                lbl[correct_index] = 1.0
                labels.append(lbl)
            model.train(np.array(data), np.array(labels), epochs=1, learning_rate=0.01, batch_size=4, verbose=False)
            model.memory.clear()

    def analyze_text(self, text, use_dlp=True):
        """
        Menganalisis teks menggunakan model AI, dan jika gagal, gunakan DLP.
        """
        features = np.array([
            len(text),
            sum(c.isdigit() for c in text),
            sum(c.isupper() for c in text)
        ])
        features = np.pad(features, (0, 7), mode='constant')
        output = self.predict("simpleAI", np.array([features]))
        actions = ["respond", "classify_error", "fix_code", "calculate", "logic_check", "text_output"]

        if output is not None:
            top_action = actions[int(np.argmax(output))]
            return {"text": text, "output": top_action, "confidence": float(np.max(output))}

        # Jika output None, fallback ke DLP (TextBlob)
        if use_dlp:
            return self.dlp.process(text)

        return {"text": text, "output": "unknown", "confidence": 0.0}
