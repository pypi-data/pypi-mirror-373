# dearning/__init__.py
from .model import CustomAIModel, Dense, Activation, Dropout, DOtensor
from .utils import preprocess_data, evaluate_model, Optimizer
from .training import LogEkstrainnix
from .Quantum import Quantum
from .AI_tools import DLP, AImemory, TTS, RLTools, Qanalyze
from .AI_core import CodeTracker, BinaryConverter, ByteConverter
from .multymodel import AImodel
from .testing import test_model


# === 🔄 Lazy Loader Util ===
import importlib, sys, builtins

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

_testing = _LazyLoader("dearning.testing", [
    "test_model"
])

_utils = _LazyLoader("dearning.utils", [
    "preprocess_data", "evaluate_model", "Optimizer"
])

_training = _LazyLoader("dearning.training", [
    "logEkstrainnix"
])

_AI_tools = _LazyLoader("dearning.AI_tools", [
    "DLP", "AImemory", "TTS", "RLTools", "Qanalyze"
])

_AI_core = _LazyLoader("dearning.AI_core", [
    "CodeTracker", "BinaryConverter", "ByteConverter"
])

_multymodel = _LazyLoader("dearning.multymodel", [
    "AImodel"
])

_Quantum = _LazyLoader("dearning.Quantum", [
    "Quantum"
])

# === 🌐 Public API Expose ===

CodeTracker = _AI_core.CodeTracker
BinaryConverter = _AI_core.BinaryConverter
ByteConverter = _AI_core.ByteConverter

AImodel = _multymodel.AImodel
