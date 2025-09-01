# dearning/__init__.py
import importlib, builtins

# === 🛡️ Protection ===
builtins.__dafe_protect__ = True

class _LazyLoader:
    def __init__(self, module_name, exports):
        self._module_name = module_name
        self._exports = exports
        self._module = None

    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self._module_name)
        return self._module

    def __getattr__(self, attr):
        if attr in self._exports:
            return getattr(self._load(), attr)
        raise AttributeError(f"'{self._module_name}' has no attribute '{attr}'")

# === 📦 Register Lazy Modules ===
_model = _LazyLoader("dearning.model", [
    "CustomAIModel", "Dense", "Activation", "Dropout", "DOtensor"
])

_utils = _LazyLoader("dearning.utils", [
    "preprocess_data", "evaluate_model"
])

_training = _LazyLoader("dearning.training", [
    "LogEkstrainnix"
])

_AI_tools = _LazyLoader("dearning.AI_tools", [
    "DLP", "AImemory", "TTS", "RLTools", "Qkanalyze", "video"
])

_AI_core = _LazyLoader("dearning.AI_core", [
    "CodeTracker", "BinaryConverter", "ByteConverter"
])

_multymodel = _LazyLoader("dearning.multymodel", [
    "AImodel"
])

_quantum = _LazyLoader("dearning.Quantum", [
    "Quantum"
])

_testing = _LazyLoader("dearning.testing", [
    "test_model"
])

# === 🌐 Public API Expose ===
CustomAIModel = _model.CustomAIModel
Dense = _model.Dense
Activation = _model.Activation
Dropout = _model.Dropout
DOtensor = _model.DOtensor

preprocess_data = _utils.preprocess_data
evaluate_model = _utils.evaluate_model

LogEkstrainnix = _training.LogEkstrainnix

DLP = _AI_tools.DLP
AImemory = _AI_tools.AImemory
TTS = _AI_tools.TTS
RLTools = _AI_tools.RLTools
video = _AI_tools.video
Qkanalyze = _AI_tools.Qkanalyze

CodeTracker = _AI_core.CodeTracker
BinaryConverter = _AI_core.BinaryConverter
ByteConverter = _AI_core.ByteConverter

AImodel = _multymodel.AImodel
Quantum = _quantum.Quantum

test_model = _testing.test_model
