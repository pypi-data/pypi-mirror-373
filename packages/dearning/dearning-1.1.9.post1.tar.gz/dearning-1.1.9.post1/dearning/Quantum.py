import numpy as np
import math, cmath, asyncio, functools, itertools, bisect, statistics, logging, time, os, atexit
from decimal import Decimal
from fractions import Fraction
from scipy.linalg import expm, norm
from multiprocessing import Pool, cpu_count
from array import array

class Quan:
    # ===== Aritmetika =====
    @staticmethod
    def tambah(a, b): return a + b
    @staticmethod
    def kurang(a, b): return a - b
    @staticmethod
    def kali(a, b): return a * b
    @staticmethod
    def bagi(a, b): return a / b if b != 0 else None

    # ===== Aljabar =====
    @staticmethod
    def kuadrat(x): return x**2
    @staticmethod
    def akar(x): return math.sqrt(x)

    # ===== Trigonometri =====
    @staticmethod
    def trigono(x):  
        return {
            "sin": math.sin(x),
            "cos": math.cos(x),
            "tan": math.tan(x),
            "asin": math.asin(x),
            "acos": math.acos(x),
            "atan": math.atan(x)
        }

    # ===== Logaritma & Eksponensial =====
    @staticmethod
    def logeks(x, base=math.e):
        return {
            "log": math.log(x, base),
            "exp": math.exp(x)
        }

    # ===== Pythagoras =====
    @staticmethod
    def Tphytagoras(a, b):
        return math.sqrt(a**2 + b**2)

    # ===== Matrix =====
    @staticmethod
    def matrix_mul(A, B):
        return np.dot(A, B)
    @staticmethod
    def matrix_inv(A):
        return np.linalg.inv(A)

    # ===== Geometri =====
    @staticmethod
    def luas_lingkaran(r):
        return math.pi * r**2
    @staticmethod
    def volume_bola(r):
        return (4/3) * math.pi * (r**3)

    # ===== Statistik =====
    @staticmethod
    def statistik(data):
        return {
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "stdev": statistics.pstdev(data)
        }

    # ===== Probabilitas =====
    @staticmethod
    def peluang(event, sample):
        return Fraction(event, sample)

    # ===== Kalkulus (derivatif & integral sederhana) =====
    @staticmethod
    def turunan(f, x, h=1e-5):
        return (f(x + h) - f(x - h)) / (2 * h)

    @staticmethod
    def integral(f, a, b, n=1000):
        dx = (b - a) / n
        area = 0
        for i in range(n):
            area += f(a + i*dx) * dx
        return area

    # ===== Ratio =====
    @staticmethod
    def ratio(a, b):
        return Fraction(a, b)

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Quantum:
    """
    Triplogeonorasio-Quantum-Estakaltrixalmatik (Tingkat 8 - Unstable Quantum)
    Quantum-style AI hybrid dengan kalkulus, statistika, dan matrix intensif.
    """
    def __init__(self, qubit_size=4, n_cores=2, seed: int | None = None):
        self.qubit_size = int(qubit_size)
        self.state = self.initialize()
        self.gates = []
        self.entangled_pairs = []
        self.n_cores = min(int(n_cores), cpu_count())
        self._rng = np.random.default_rng(seed)
        self._pool = None
        self.debug_compact = True
        self._damping = 0.995

    # === Representasi Quantum ===
    def initialize(self):
        vec = np.zeros((2 ** self.qubit_size,), dtype=complex)
        vec[0] = 1.0 + 0j
        return vec

    # === Quantum Gates ===
    def apply_gate(self, gate, index, adaptive=True):
        I = np.eye(2, dtype=complex)
        ops = [I] * self.qubit_size
        ops[int(index)] = gate
        full_gate = functools.reduce(np.kron, ops)
        if adaptive:
            try:
                abs_mean = float(np.mean(np.abs(self.state)))
                # simple stable scale
                scale = float(np.clip(np.exp(-min(abs_mean, 50.0)), 1e-6, 10.0))
            except Exception:
                scale = 1.0
            full_gate = full_gate * scale
        # apply
        self.state = full_gate @ self.state
        self.state *= self._damping
        self.gates.append((gate, int(index)))

    def hadamard(self, index):
        H = (1.0 / math.sqrt(2.0)) * np.array([[1, 1], [1, -1]], dtype=complex)
        self.apply_gate(H, index)

    def pauli_x(self, index):
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        asyncio.run(self.apply_gate(X, index))
    def pauli_y(self, index):
        Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        asyncio.run(self.apply_gate(Y, index))
    def pauli_z(self, index):
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        asyncio.run(self.apply_gate(Z, index))

    def cnot(self, control, target):
        n = 2 ** self.qubit_size
        for i in range(n):
            b = format(i, f'0{self.qubit_size}b')
            if b[control] == '1':
                flipped = list(b)
                flipped[target] = '0' if b[target] == '1' else '1'
                j = int(''.join(flipped), 2)
                self.state[i], self.state[j] = self.state[j], self.state[i]

    def entangle(self, q1, q2):
        pair = (int(q1), int(q2))
        if pair not in self.entangled_pairs:
            self.entangled_pairs.append(pair)

    def measure(self, top_k: int = 5):
        probs = Quan.kuadrat(np.abs(self.state))
        total = np.sum(probs)
        if total <= 0:
            probs = np.ones_like(probs) / probs.size
        else:
            probs = probs / total
        idx = int(self._rng.choice(len(probs), p=probs))
        result = np.binary_repr(idx, width=self.qubit_size)
        if self.entangled_pairs:
            rlist = list(result)
            for q1, q2 in self.entangled_pairs:
                if rlist[q1] != rlist[q2]:
                    rlist[q2] = rlist[q1]
            result = "".join(rlist)
        k = min(int(top_k), len(probs))
        top_idx = []
        for i, p in enumerate(probs):
            if len(top_idx) < k:
                bisect.insort(top_idx, (p, i))
            elif p > top_idx[0][0]:
                bisect.insort(top_idx, (p, i))
                if len(top_idx) > k:
                    top_idx.pop(0)
        top_idx_desc = [(i, float(p)) for (p, i) in reversed(top_idx)]
        probs_array = array('d', probs.tolist())
        stats = Quan.statistik(probs.tolist())
        return {
            "result": result,
            "probabilities": probs_array,
            "top_k": top_idx_desc,
            "total_prob_sum": float(total),
            "stats": {
                "mean": float(stats["mean"]),
                "median": float(stats["median"]),
                "stdev": float(stats["stdev"])
            }
        }

    @staticmethod
    def _worker_update_seeded(seed, state_chunk, factor, damping):
        # worker: menerima potongan array (kontigu) dan mengembalikan updated chunk
        rng = np.random.default_rng(seed)
        # pastikan contiguous untuk operasi cepat
        chunk = np.ascontiguousarray(state_chunk)
        # gaussian noise (real part only for complex arrays; complex noise could be added if wanted)
        noise_real = rng.normal(0.0, 0.001 * max(1.0, abs(factor)), size=chunk.shape)
        noise = noise_real.astype(chunk.dtype)  # keep dtype match (will broadcast to complex if needed)
        # updated = chunk * factor + noise; apply damping
        updated = chunk * factor
        # add noise (works for complex dtype: noise becomes real part)
        updated = updated + noise
        updated = updated * damping
        return updated

    def unstable_multiprocessing_update(self, factor: float = 1.0):
        # quick sanity
        if self.state.size == 0:
            return
        # enforce complex128 contiguous state (helps pickling speed & numeric stability)
        if self.state.dtype != np.complex128:
            self.state = self.state.astype(np.complex128)
        self.state = np.ascontiguousarray(self.state)

        # choose cores (max 2 as requested)
        n_cores = max(1, min(2, int(self.n_cores)))
        # split into contiguous chunks
        chunks = np.array_split(self.state, n_cores)
        # prepare seeds and args (make chunk contiguous to reduce pickle overhead)
        seeds = [int(self._rng.integers(0, 2**31 - 1)) for _ in range(len(chunks))]
        args = [(s, np.ascontiguousarray(c), float(factor), float(self._damping))
                for s, c in zip(seeds, chunks)]

        # create persistent pool if not exists
        if getattr(self, "_pool", None) is None:
            import os
            # limit BLAS/OMP threads in workers to avoid oversubscription
            os.environ.setdefault("OMP_NUM_THREADS", "1")
            os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
            os.environ.setdefault("MKL_NUM_THREADS", "1")
            from multiprocessing import Pool
            # create pool once and reuse it; maxtasksperchild to mitigate leaks
            self._pool = Pool(processes=n_cores, maxtasksperchild=200)
        # run workers (starmap will pickle args; chunks are contiguous which speeds this up)
        results = self._pool.starmap(Quantum._worker_update_seeded, args)
        # concatenate results and renormalize
        self.state = np.concatenate(results)
        norm_val = np.linalg.norm(self.state)
        if norm_val > 0:
            self.state = self.state / norm_val


    def grover(self, oracle_mask_or_fn):
        N = len(self.state)
        # build mask
        if callable(oracle_mask_or_fn):
            mask = oracle_mask_or_fn(self.state)
        else:
            mask = np.asarray(oracle_mask_or_fn, dtype=bool)
        # prepare hadamard on all qubits
        H = (1.0 / math.sqrt(2.0)) * np.array([[1, 1], [1, -1]], dtype=complex)
        for i in range(self.qubit_size):
            self.apply_gate(H, i)
        iterations = int(np.floor(np.pi/4 * math.sqrt(N)))
        for _ in range(iterations):
            # oracle: flip phase
            self.state[mask] *= -1
            # diffusion: reflect about mean amplitude
            mean_amp = np.mean(self.state)
            self.state = 2*mean_amp - self.state
        return self.measure()

    def shor(self, n):
        return f"Factoring {n} (simulated)"

    def qft(self):
        N = len(self.state)
        self.state = np.fft.fft(self.state) / math.sqrt(N)
        norm_val = np.linalg.norm(self.state)
        if norm_val > 0:
            self.state /= norm_val
        return self.measure()

    def vqe(self, cost_function, iterations: int = 10):
        loss = None
        for i in range(int(iterations)):
            self.unstable_multiprocessing_update(factor=1.0)
            loss = float(cost_function(self.state))
            if self.debug_compact:
                _log.info(f"[VQE] iter={i+1}/{iterations} loss={loss:.6f}")
        return {"state": self.state, "loss": loss}

    def qaoa(self, hamiltonian, iterations: int = 10):
        for i in range(int(iterations)):
            try:
                self.state = Quan.matrix_mul(expm(Quan.kali(-1j, hamiltonian)), self.state)
            except Exception:
                mean_diag = np.mean(np.diag(hamiltonian))
                self.state = Quan.kali(self.state, np.exp(Quan.kali(-1j, mean_diag)))
            self.unstable_multiprocessing_update(factor=0.99)
        return self.measure()

    def debug_state(self, top_n: int = 5):
        meas = self.measure(top_k=top_n)
        _log.info("🔹 Quantum State Summary:")
        _log.info(f"  bitstring (sampled) : {meas['result']}")
        _log.info(f"  top_{top_n}          : {meas['top_k']}")
        stats = meas.get("stats", {})
        _log.info(f"  probs mean/median/stdev : {stats.get('mean'):.6e} / {stats.get('median'):.6e} / {stats.get('stdev'):.6e}")
        _log.info(f"  gates applied count     : {len(self.gates)}")
        _log.info(f"  entangled pairs         : {self.entangled_pairs}")

    def compact_summary(self, top_n: int = 5):
        meas = self.measure(top_k=top_n)
        return {
            "sampled_bitstring": meas["result"],
            "top_k": meas["top_k"],
            "stats": meas["stats"],
            "gates_applied": len(self.gates),
            "entangled_pairs": list(self.entangled_pairs)
        }

    def reset(self):
        self.state = self.initialize()
        self.gates.clear()
        self.entangled_pairs.clear()

    def summary(self):
        stats = {
            "qubit_size": self.qubit_size,
            "gates_applied": len(self.gates),
            "entangled_pairs": list(self.entangled_pairs),
            "state_norm": float(np.linalg.norm(self.state))
        }
        return stats

if __name__ == "__main__":
    # pastikan BLAS thread limit juga di runner (opsional)
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    # buat instance Quantum
    q = Quantum(qubit_size=6, n_cores=2, seed=12345)
    try:
        # contoh operasi
        q.hadamard(0)
        q.hadamard(1)
        print("Before update:", q.compact_summary(top_n=3))
        # jalankan multiprocessing update (akan membuat/ reuse pool)
        t0 = time.perf_counter()
        q.unstable_multiprocessing_update(factor=1.0)
        t1 = time.perf_counter()
        print(f"Multiproc update took {t1-t0:.4f}s")
        print("After update:", q.compact_summary(top_n=3))

        # contoh Grover dengan mask sederhana (pastikan panjang sama)
        N = len(q.state)
        # contoh: tandai satu indeks (mis. index 3)
        mask = np.zeros(N, dtype=bool)
        mask[3] = True
        res = q.grover(mask)
        print("Grover measured:", res["result"])
    finally:
        # IMPORTANT: tutup pool supaya child process tidak menggantung
        def close_pool(self):
            if getattr(self, "_pool", None) is not None:
                self._pool.close()
                self._pool.join()
                self._pool = None
        q.close_pool()    
        atexit.register(lambda: q.close_pool())