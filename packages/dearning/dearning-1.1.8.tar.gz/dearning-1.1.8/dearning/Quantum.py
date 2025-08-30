import numpy as np
import math, cmath, asyncio, functools, itertools, bisect, statistics, logging
from decimal import Decimal
from fractions import Fraction
from scipy.linalg import expm, norm
from multiprocessing import Pool, cpu_count
from array import array

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
        # RNG per-instance untuk konsistensi (default np random Generator)
        self._rng = np.random.default_rng(seed)
        # compact debug control
        self.debug_compact = True
        # small damping to keep unstable updates under control
        self._damping = 0.995

    # === Representasi Quantum ===
    def initialize(self):
        vec = np.zeros((2 ** self.qubit_size,), dtype=complex)
        vec[0] = 1.0 + 0j
        return vec

    # === Quantum Gates ===
    async def apply_gate(self, gate, index, adaptive=True):
        # build full gate by kron; if qubit_size grows big this is expensive
        I = np.eye(2, dtype=complex)
        ops = [I] * self.qubit_size
        ops[int(index)] = gate
        full_gate = functools.reduce(np.kron, ops)
        if adaptive:
            # use whole-state statistic for scaling to improve numeric stability
            try:
                abs_mean = np.mean(np.abs(self.state))
                # damping + bounded scale to avoid overflow
                scale = np.exp(-min(abs_mean, 50.0)) * (1.0 + math.sin(min(abs_mean, 50.0)))
                scale = float(np.clip(scale, 1e-6, 10.0))
            except Exception:
                scale = 1.0
            full_gate = full_gate * scale
        # apply gate (matrix-vector)
        self.state = full_gate @ self.state
        # small global damping to keep amplitudes numerically stable
        self.state *= self._damping
        self.gates.append((gate, int(index)))

    # synchronous wrappers (kept for API compatibility)
    def hadamard(self, index):
        H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
        asyncio.run(self.apply_gate(H, index))

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
        # inplace swap amplitudes for classical CNOT effect
        n = 2 ** self.qubit_size
        # iterate indices and swap the pair when control bit is 1
        for i in range(n):
            b = format(i, f'0{self.qubit_size}b')
            if b[control] == '1':
                flipped = list(b)
                flipped[target] = '0' if b[target] == '1' else '1'
                j = int(''.join(flipped), 2)
                # swap amplitudes
                self.state[i], self.state[j] = self.state[j], self.state[i]

    # === Entanglement ===
    def entangle(self, q1, q2):
        pair = (int(q1), int(q2))
        if pair not in self.entangled_pairs:
            self.entangled_pairs.append(pair)

    # === Measurement ===
    def measure(self, top_k: int = 5):
        """
        Measure state:
         - return dict { "result": bitstring, "probabilities": probs }
         - provide fast top-k summary using bisect (O(n log k)) instead of full sort.
        """
        probs = np.abs(self.state) ** 2
        total = probs.sum()
        if total <= 0:
            # degenerate case: fallback uniform distribution
            probs = np.ones_like(probs) / probs.size
        else:
            probs = probs / total  # normalize

        # sample index according to probs using RNG.choice
        idx = int(self._rng.choice(len(probs), p=probs))
        result = np.binary_repr(idx, width=self.qubit_size)

        # enforce entanglement constraints (simple rule: copy control->target)
        if self.entangled_pairs:
            rlist = list(result)
            for q1, q2 in self.entangled_pairs:
                if rlist[q1] != rlist[q2]:
                    rlist[q2] = rlist[q1]
            result = "".join(rlist)

        # top-k probs via bisect (efficient when k << n)
        k = min(int(top_k), len(probs))
        top_idx = []  # will store tuples (prob, index) in ascending prob order
        for i, p in enumerate(probs):
            if len(top_idx) < k:
                bisect.insort(top_idx, (p, i))
            elif p > top_idx[0][0]:
                # replace smallest in top_idx
                bisect.insort(top_idx, (p, i))
                # trim to k
                if len(top_idx) > k:
                    top_idx.pop(0)

        # convert into descending order list
        top_idx_desc = [(i, float(p)) for (p, i) in reversed(top_idx)]
        # store probabilities in memory-efficient array of doubles for quick inspection
        probs_array = array('d', probs.tolist())
        return {
            "result": result,
            "probabilities": probs_array,
            "top_k": top_idx_desc,
            "total_prob_sum": float(total),
            "stats": {
                "mean": float(statistics.mean(probs.tolist())),
                "median": float(statistics.median(probs.tolist())),
                "stdev": float(statistics.pstdev(probs.tolist()))  # population stdev
            }
        }

    # === Unstable Quantum Utilities ===
    @staticmethod
    def _worker_update_seeded(seed, state_chunk, factor, damping):
        """
        Worker function used in multiprocessing -> seeded RNG and returns updated chunk.
        Provided as top-level staticmethod style for pickling through Pool.
        """
        rng = np.random.default_rng(seed)
        # add gaussian noise small scale, but scaled by factor
        noise = rng.normal(0.0, 0.001 * max(1.0, abs(factor)), size=state_chunk.shape)
        updated = state_chunk * factor + noise
        # apply damping on chunk to control growth
        return updated * damping

    def unstable_multiprocessing_update(self, factor: float = 1.0):
        """
        Update state across n_cores using multiprocessing.Pool.
        Worker seeds are derived from instance RNG to allow reproducibility.
        """
        chunks = np.array_split(self.state, self.n_cores)
        # prepare seeds from instance RNG
        seeds = [int(self._rng.integers(0, 2**31 - 1)) for _ in range(self.n_cores)]
        args = [(s, c, float(factor), float(self._damping)) for s, c in zip(seeds, chunks)]
        # starmap to static worker function
        with Pool(processes=self.n_cores) as pool:
            results = pool.starmap(Quantum._worker_update_seeded, args)
        self.state = np.concatenate(results)
        # renormalize state to avoid drift
        norm_val = np.linalg.norm(self.state)
        if norm_val > 0:
            self.state = self.state / norm_val

    # === Algoritma Quantum Terintegrasi ===
    def grover(self, oracle):
        N = len(self.state)
        H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
        for i in range(self.qubit_size):
            asyncio.run(self.apply_gate(H, i))
        iterations = int(np.floor(np.pi / 4 * np.sqrt(N)))
        for _ in range(iterations):
            # simplified oracle reflection step (user-provided oracle should be compatible)
            try:
                # keep numeric stable by clipping large values
                reflect = self.state @ oracle(self.state)
                reflect = np.clip(reflect, -1e6, 1e6)
                self.state = self.state * 2 - reflect * 2
            except Exception:
                # fallback simple amplitude flip
                self.state = -self.state
        return self.measure()

    def shor(self, n):
        # placeholder simulation remain same API
        return f"Factoring {n} (simulated)"

    def qft(self):
        N = len(self.state)
        omega = np.exp(2j * np.pi / N)
        qft_matrix = np.array([[omega ** (i * j) / np.sqrt(N) for j in range(N)] for i in range(N)], dtype=complex)
        self.state = qft_matrix @ self.state
        # renormalize and return measurement
        norm_val = np.linalg.norm(self.state)
        if norm_val > 0:
            self.state = self.state / norm_val
        return self.measure()

    def vqe(self, cost_function, iterations: int = 10):
        """VQE hybrid dengan Unstable Quantum update multiprocessing"""
        loss = None
        for i in range(int(iterations)):
            self.unstable_multiprocessing_update(factor=1.0)
            loss = float(cost_function(self.state))
            if self.debug_compact:
                _log.info(f"[VQE] iter={i+1}/{iterations} loss={loss:.6f}")
        return {"state": self.state, "loss": loss}

    def qaoa(self, hamiltonian, iterations: int = 10):
        for i in range(int(iterations)):
            # apply Hamiltonian evolution (matrix exponential)
            try:
                self.state = expm(-1j * hamiltonian) @ self.state
            except Exception:
                # fallback to simple linear evolution if hamiltonian is invalid
                self.state = self.state * np.exp(-1j * np.mean(np.diag(hamiltonian)))
            self.unstable_multiprocessing_update(factor=0.99)
        return self.measure()

    # === Debug / Utility ===
    def debug_state(self, top_n: int = 5):
        """Print compact state summary (top probabilities + stats)."""
        meas = self.measure(top_k=top_n)
        _log.info("🔹 Quantum State Summary:")
        _log.info(f"  bitstring (sampled) : {meas['result']}")
        _log.info(f"  top_{top_n}          : {meas['top_k']}")
        stats = meas.get("stats", {})
        _log.info(f"  probs mean/median/stdev : {stats.get('mean'):.6e} / {stats.get('median'):.6e} / {stats.get('stdev'):.6e}")
        _log.info(f"  gates applied count     : {len(self.gates)}")
        _log.info(f"  entangled pairs         : {self.entangled_pairs}")

    def compact_summary(self, top_n: int = 5):
        """Return compact summary dict (no prints)"""
        meas = self.measure(top_k=top_n)
        return {
            "sampled_bitstring": meas["result"],
            "top_k": meas["top_k"],
            "stats": meas["stats"],
            "gates_applied": len(self.gates),
            "entangled_pairs": list(self.entangled_pairs)
        }

    # === Utility ===
    def reset(self):
        self.state = self.initialize()
        self.gates.clear()
        self.entangled_pairs.clear()

    def summary(self):
        # be careful returning very large state; return compact statistics instead
        stats = {
            "qubit_size": self.qubit_size,
            "gates_applied": len(self.gates),
            "entangled_pairs": list(self.entangled_pairs),
            "state_norm": float(np.linalg.norm(self.state))
        }
        return stats
