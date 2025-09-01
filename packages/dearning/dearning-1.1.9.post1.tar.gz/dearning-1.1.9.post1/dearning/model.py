import numpy as np
import json, os, threading
from scipy.signal import convolve
import networkx as nx

class DOtensor:
    _global_trace_enabled = False
    _global_trace_log = []

    def _init_(self, data, requires_grad=False):
        self.data = np.array(data, dtype=float, copy=False)  # hindari copy berlebih
        self.requires_grad = requires_grad
        self.grad = np.zeros_like(self.data) if requires_grad else None
        self._backward = lambda: None
        self._prev = ()

    def _add_(self, other):
        other = other if isinstance(other, DOtensor) else DOtensor(other)
        out = DOtensor(self.data + other.data, requires_grad=(self.requires_grad or other.requires_grad))

        if out.requires_grad:
            def _backward():
                if self.requires_grad:
                    self.grad += out.grad
                if other.requires_grad:
                    other.grad += out.grad
            out._backward = _backward
            out._prev = (self, other)

        if DOtensor._global_trace_enabled:
            DOtensor._global_trace_log.append(("add", self.data, other.data))
        return out

    def _mul_(self, other):
        other = other if isinstance(other, DOtensor) else DOtensor(other)
        out = DOtensor(self.data * other.data, requires_grad=(self.requires_grad or other.requires_grad))

        if out.requires_grad:
            def _backward():
                if self.requires_grad:
                    self.grad += other.data * out.grad
                if other.requires_grad:
                    other.grad += self.data * out.grad
            out._backward = _backward
            out._prev = (self, other)

        if DOtensor._global_trace_enabled:
            DOtensor._global_trace_log.append(("mul", self.data, other.data))
        return out

    def backward(self):
        if not self.requires_grad:
            raise RuntimeError("backward() called on tensor without requires_grad")

        self.grad = np.ones_like(self.data)
        stack = [self]
        visited = set()

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                node._backward()
                stack.extend(node._prev)

    def _repr_(self):
        return f"DOtensor(data={self.data}, grad={self.grad})"

    @staticmethod
    def enable_trace():
        DOtensor._global_trace_enabled = True
        DOtensor._global_trace_log = []

    @staticmethod
    def disable_trace():
        DOtensor._global_trace_enabled = False

    @staticmethod
    def get_trace_log():
        return list(DOtensor._global_trace_log)  # copy ringan

# === Modular Layer Base ===
class Layer:
    def forward(self, x): raise NotImplementedError
    def backward(self, grad): raise NotImplementedError
    def update(self, lr): pass

# === Dense Layer ===
class Dense(Layer):
    def __init__(self, input_dim, output_dim):
        self.weights = np.random.randn(input_dim, output_dim) * np.sqrt(2. / input_dim)
        self.bias = np.zeros((1, output_dim))

    def forward(self, x):
        self.input = x
        self.output = np.dot(x, self.weights) + self.bias
        return self.output

    def backward(self, grad_output):
        self.grad_w = np.dot(self.input.T, grad_output)
        self.grad_b = np.sum(grad_output, axis=0, keepdims=True)
        return np.dot(grad_output, self.weights.T)

    def update(self, lr):
        self.weights -= lr * self.grad_w
        self.bias -= lr * self.grad_b

# === Activation Layer ===
class Activation(Layer):
    def __init__(self, kind="relu"):
        self.kind = kind

    def forward(self, x):
        self.input = x
        if self.kind == "relu":
            return np.maximum(0, x)
        elif self.kind == "sigmoid":
            return 1 / (1 + np.exp(-x))
        elif self.kind == "tanh":
            return np.tanh(x)
        return x

    def backward(self, grad_output):
        if self.kind == "relu":
            return grad_output * (self.input > 0)
        elif self.kind == "sigmoid":
            s = 1 / (1 + np.exp(-self.input))
            return grad_output * s * (1 - s)
        elif self.kind == "tanh":
            return grad_output * (1 - np.tanh(self.input)**2)
        return grad_output

# === Dropout (Opsional) ===
class Dropout(Layer):
    def __init__(self, rate=0.5):
        self.rate = rate

    def forward(self, x):
        self.mask = (np.random.rand(*x.shape) > self.rate).astype(float)
        return x * self.mask

    def backward(self, grad_output):
        return grad_output * self.mask

# === Custom Model ===
class CustomAIModel:
    def __init__(self, loss="mse"):
        self.layers = []
        self.loss = loss
        self.losses = []
        self.memory_neuron = None
        self.expert_neurons = []

    def add(self, layer):
        self.layers.append(layer)

    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x

    def addneuron(self, kind="memory", **kwargs):
        """
        Menambahkan neuron khusus ke model.

        kind: Jenis neuron yang ditambahkan.
        kwargs: Parameter tambahan spesifik neuron.
        """

        if kind == "memory":
            size = kwargs.get("size", 128)
            self.memory_neuron = np.zeros((1, size))
            print(f"🧠 Neuron Memory ditambahkan (size={size})")

        elif kind == "attention":
            def attention(query, keys, values):
                scores = np.dot(query, keys.T)
                weights = np.exp(scores) / np.sum(np.exp(scores), axis=1, keepdims=True)
                return np.dot(weights, values)
            self.attention = attention
            print("🎯 Neuron Attention ditambahkan")

        elif kind == "ntc":            
            def ntc_layer(x, kernel):
                return convolve(x, kernel, mode='same')
            self.ntc = lambda x: ntc_layer(x, kwargs.get("kernel", np.array([1, -1, 1])))
            print("🕒 Neuron Temporal Convolution ditambahkan")

        elif kind == "graph":            
            self.graph = nx.Graph()
            self.graph.add_nodes_from(kwargs.get("nodes", [0, 1]))
            self.graph.add_edges_from(kwargs.get("edges", [(0, 1)]))
            print("🔗 Neuron Graph ditambahkan")

        elif kind == "nalu":
            def nalu(x):
                eps = 1e-7
                g = np.tanh(x)
                a = np.dot(x, kwargs.get("W_a", np.ones((x.shape[1], 1))))
                m = np.exp(np.dot(np.log(np.abs(x) + eps), kwargs.get("W_m", np.ones((x.shape[1], 1)))))
                return g * a + (1 - g) * m
            self.nalu = nalu
            print("🧮 Neuron NALU (Arithmetic Logic) ditambahkan")

        elif kind == "moe":
            experts = kwargs.get("experts", [lambda x: x])
            gate = kwargs.get("gate", lambda x: [1/len(experts)]*len(experts))
            def moe(x):
                weights = gate(x)
                return sum(w * e(x) for w, e in zip(weights, experts))
            self.expert_neurons.append(moe)
            print("👥 Neuron Mixture of Experts ditambahkan")

        elif kind == "spiking":
            def spiking(x, threshold=0.5):
                spikes = (x > threshold).astype(float)
                return spikes
            self.spiking = spiking
            print("⚡ Neuron Spiking ditambahkan (threshold=0.5)")

        else:
            print(f"❌ Neuron {kind} tidak dikenal.")

    def _loss(self, y_pred, y_true):
        if self.loss == "mse":
            return np.mean((y_pred - y_true) ** 2)
        elif self.loss == "cross_entropy":
            epsilon = 1e-8
            return -np.mean(y_true * np.log(y_pred + epsilon) + (1 - y_true) * np.log(1 - y_pred + epsilon))
        return 0

    def _loss_grad(self, y_pred, y_true):
        if self.loss == "mse":
            return 2 * (y_pred - y_true) / y_true.shape[0]
        elif self.loss == "cross_entropy":
            return (y_pred - y_true) / y_true.shape[0]
        return 0

    def train(self, X, y, epochs=100, learning_rate=0.01, batch_size=None, verbose=True):
        n = X.shape[0]
        if batch_size is None: batch_size = n

        for epoch in range(epochs):
            indices = np.random.permutation(n)
            X, y = X[indices], y[indices]

            losses = []

            for start in range(0, n, batch_size):
                end = start + batch_size
                x_batch = X[start:end]
                y_batch = y[start:end]

                y_pred = self.forward(x_batch)
                loss = self._loss(y_pred, y_batch)
                losses.append(loss)

                grad = self._loss_grad(y_pred, y_batch)
                for layer in reversed(self.layers):
                    grad = layer.backward(grad)
                for layer in self.layers:
                    layer.update(learning_rate)

            mean_loss = np.mean(losses)
            self.losses.append(mean_loss)
            if verbose:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {mean_loss:.4f}")

    def save_model(self, path):
        config = {
            "loss": self.loss,
            "layers": [
                {"type": type(layer).__name__,
                 "params": {
                     "input_dim": getattr(layer, "weights", None).shape[0] if hasattr(layer, "weights") else None,
                     "output_dim": getattr(layer, "weights", None).shape[1] if hasattr(layer, "weights") else None,
                     "activation": getattr(layer, "kind", None),
                     "rate": getattr(layer, "rate", None)
                 }
                } for layer in self.layers
            ]
        }
        with open(path + "_config.json", "w") as f:
            json.dump(config, f)

        weights = []
        for layer in self.layers:
            if hasattr(layer, "weights"):
                weights.append(layer.weights)
                weights.append(layer.bias)
        np.savez(path + "_weights.npz", *weights)

    @classmethod
    def load_model(cls, path):
        with open(path + "_config.json", "r") as f:
            config = json.load(f)

        model = cls(loss=config["loss"])
        for layer_cfg in config["layers"]:
            if layer_cfg["type"] == "Dense":
                model.add(Dense(layer_cfg["params"]["input_dim"], layer_cfg["params"]["output_dim"]))
            elif layer_cfg["type"] == "Activation":
                model.add(Activation(layer_cfg["params"]["activation"]))
            elif layer_cfg["type"] == "Dropout":
                model.add(Dropout(layer_cfg["params"]["rate"]))

        data = np.load(path + "_weights.npz", allow_pickle=True)
        idx = 0
        for layer in model.layers:
            if hasattr(layer, "weights"):
                layer.weights = data[f"arr_{idx}"]
                layer.bias = data[f"arr_{idx+1}"]
                idx += 2
        return model                