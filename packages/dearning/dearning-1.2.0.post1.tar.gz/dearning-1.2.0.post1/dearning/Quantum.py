import numpy as np, math, cmath, asyncio, functools, itertools, bisect, statistics, logging, time, os, atexit, gc, weakref, tracemalloc
from decimal import Decimal
from fractions import Fraction
from scipy.linalg import expm, norm
try:
    from scipy.sparse.linalg import expm_multiply
except Exception:
    expm_multiply = None
from multiprocessing import Pool, cpu_count
from array import array

class Quan:
    @staticmethod
    def tambah(a, b): return a + b
    @staticmethod
    def kurang(a, b): return a - b
    @staticmethod
    def kali(a, b): return a * b
    @staticmethod
    def bagi(a, b): return a / b if b != 0 else None

    @staticmethod
    def kuadrat(x): return x**2
    @staticmethod
    def akar(x): return math.sqrt(x)

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

    @staticmethod
    def logeks(x, base=math.e):
        return {"log": math.log(x, base), "exp": math.exp(x)}

    @staticmethod
    def Tphytagoras(a, b, c=0):
        return math.sqrt(a**2 + b**2 + c**2)

    @staticmethod
    def matrix_mul(A, B):
        return np.dot(A, B)

    @staticmethod
    def matrix_inv(A):
        try:
            return np.linalg.inv(A)
        except np.linalg.LinAlgError:
            return np.linalg.pinv(A)

    @staticmethod
    def luas_lingkaran(r):
        return math.pi * r**2
    @staticmethod
    def volume_bola(r):
        return (4/3) * math.pi * (r**3)

    @staticmethod
    def statistik(data):
        data = list(data)
        return {
            "mean": statistics.mean(data) if data else 0.0,
            "median": statistics.median(data) if data else 0.0,
            "stdev": statistics.pstdev(data) if len(data) > 0 else 0.0
        }

    @staticmethod
    def peluang(event, sample):
        return Fraction(event, sample)

    @staticmethod
    def turunan(f, x, h=1e-5):
        return (f(x + h) - f(x - h)) / (2 * h)

    @staticmethod
    def integral(f, a, b, n=1000):
        dx = (b - a) / n
        area = 0.0
        for i in range(n):
            area += f(a + i*dx) * dx
        return area

    @staticmethod
    def ratio(a, b):
        return Fraction(a, b)

    # ======= Absolute Quan additions =======

    @staticmethod
    def Erelatif(m_vector, c: float = 299792458.0):
        """
        E = m c^2, vectorized.
        m_vector: scalar or array-like (kg)
        returns np.array of floats
        """
        m = np.asarray(m_vector, dtype=float)
        return m * (float(c) ** 2)

    @staticmethod
    def Efoton(f_vector, h: float = 6.62607015e-34):
        """
        E = h f, vectorized.
        f_vector: scalar or array-like (Hz)
        """
        f = np.asarray(f_vector, dtype=float)
        return float(h) * f

    @staticmethod
    def compress_array(x, M=None):
        """
        Log-compress array to avoid huge amplitudes:
        compress(x) = sign(x) * log(1 + |x|/M)
        If M not provided, use median(abs(x)) + eps.
        """
        arr = np.asarray(x, dtype=float)
        eps = 1e-12
        if M is None:
            median = np.median(np.abs(arr)) + eps
            M = max(median, eps)
        sign = np.sign(arr)
        return sign * np.log1p(np.abs(arr) / M)

    @staticmethod
    def build_C_vector(N, T_vals=None, P3_vals=None, L_vals=None, M_vals=None,
                       GeomAlg_vals=None, S_vals=None, Calc_vals=None, B_vals=None,
                       fallback_random=False):
        """
        Build C_i vector (length N) by combining provided component arrays.
        Any component not provided is treated as zeros (or random if fallback_random=True).
        Returns complex128 vector (real part from components).
        """
        def _safe_vec(v):
            if v is None:
                return np.zeros(N, dtype=float)
            v = np.asarray(v, dtype=float)
            if v.size == 1:
                return np.full(N, float(v), dtype=float)
            if v.size != N:
                # try broadcast if possible
                return np.resize(v, N).astype(float)
            return v
        if fallback_random:
            rng = np.random.default_rng()
            rand = rng.normal(0, 1, size=N)
        else:
            rand = np.zeros(N)

        T = _safe_vec(T_vals)
        P3 = _safe_vec(P3_vals)
        L = _safe_vec(L_vals)
        M_ = _safe_vec(M_vals)
        GeomAlg = _safe_vec(GeomAlg_vals)
        S = _safe_vec(S_vals)
        Calc = _safe_vec(Calc_vals)
        B = _safe_vec(B_vals)

        # Combine (this is a simple linear combination; you may replace weights as needed)
        combined = T + P3 + L + M_ + GeomAlg + S + Calc + B + rand
        # compress to control dynamic range
        compressed = Quan.compress_array(combined)
        # return complex amplitudes (imag part zero for now)
        return compressed.astype(np.complex128)

    @staticmethod
    def build_H_eff(E_rel_vec, E_ph_vec, interaction_matrix=None, coupling_scale=1e-6, cutoff=None):
        """
        Build effective Hamiltonian:
        H_eff = diag(E_rel + E_ph) + coupling_scale * (interaction_matrix truncated)
        - E_rel_vec, E_ph_vec: array-like length N
        - interaction_matrix: NxN array-like or None
        - cutoff: optional threshold to zero small couplings
        Returns NxN complex128 matrix
        """
        E_rel = np.asarray(E_rel_vec, dtype=float)
        E_ph = np.asarray(E_ph_vec, dtype=float)
        N = E_rel.shape[0]
        H = np.diag(E_rel + E_ph).astype(np.complex128)
        if interaction_matrix is not None:
            A = np.asarray(interaction_matrix, dtype=float)
            if A.shape != (N, N):
                # try to resize or embed
                A2 = np.zeros((N, N), dtype=float)
                small = A.shape
                A2[:small[0], :small[1]] = A[:N, :N]
                A = A2
            # apply cutoff
            if cutoff is not None:
                A[np.abs(A) < float(cutoff)] = 0.0
            H += coupling_scale * A.astype(np.complex128)
        return H

    @staticmethod
    def expm_apply(H, state):
        """
        Apply unitary U = exp(i H) to state efficiently if possible.
        If scipy.sparse.linalg.expm_multiply available, use it.
        Otherwise compute expm(iH) @ state (ok for small-medium H).
        """
        state = np.asarray(state, dtype=np.complex128)
        N = state.shape[0]
        # make H hermitian (symmetrize) to avoid numeric weirdness
        Hc = (H + H.conj().T) / 2.0
        # apply i*H
        mat = 1j * Hc
        if expm_multiply is not None:
            try:
                # expm_multiply handles (matrix, vector) product without forming full expm
                return expm_multiply(mat, state)
            except Exception:
                pass
        # fallback
        U = expm(mat)
        return U @ state

    @staticmethod
    def qft(state):
        """
        Simple QFT via FFT (vectorized) with normalization so that it's unitary.
        """
        st = np.asarray(state, dtype=np.complex128)
        N = st.shape[0]
        # numpy FFT is not unitary by default; scale by 1/sqrt(N)
        return np.fft.fft(st) / math.sqrt(N)

    @staticmethod
    def variational_layer(state, phase_params=None):
        """
        Very simple variational layer: multiply each amplitude by a phase exp(i * theta_i)
        - phase_params can be scalar or vector of length N; if None, small random phases applied
        """
        st = np.asarray(state, dtype=np.complex128)
        N = st.shape[0]
        if phase_params is None:
            rng = np.random.default_rng()
            phase = rng.normal(0.0, 0.01, size=N)
        else:
            p = np.asarray(phase_params, dtype=float)
            if p.size == 1:
                phase = np.full(N, float(p), dtype=float)
            else:
                phase = np.resize(p, N)
        return st * np.exp(1j * phase)

    @staticmethod
    def normalize(state, eps_adaptive=None):
        st = np.asarray(state, dtype=np.complex128)
        n = np.linalg.norm(st)
        if eps_adaptive is None:
            eps = 1e-12
        else:
            eps = float(eps_adaptive)
        if n <= eps:
            return st  # degenerate
        return st / n

    @staticmethod
    def measure_topk(state, rng=None, top_k=5):
        """
        Return dict with sampled bitstring (index), probabilities array, top_k list and stats.
        """
        st = np.asarray(state, dtype=np.complex128)
        probs = np.abs(st) ** 2
        total = float(np.sum(probs))
        if total <= 0:
            probs = np.ones_like(probs) / probs.size
        else:
            probs = probs / total
        if rng is None:
            rng = np.random.default_rng()
        idx = int(rng.choice(len(probs), p=probs))
        bitstr = np.binary_repr(idx, width=int(math.log2(len(probs))))
        # top-k
        k = min(max(1, int(top_k)), len(probs))
        # use partial selection (np.argpartition) then sort
        idxs = np.argpartition(-probs, k-1)[:k]
        sorted_top = sorted([(int(i), float(probs[i])) for i in idxs], key=lambda x: -x[1])
        stats = {
            "mean": float(np.mean(probs)),
            "median": float(np.median(probs)),
            "stdev": float(np.std(probs))
        }
        return {
            "result_index": idx,
            "result_bitstring": bitstr,
            "probabilities": probs,
            "top_k": sorted_top,
            "stats": stats
        }

    @staticmethod
    def step_absolute(state,
                      m_vec=None, f_vec=None, interaction_matrix=None,
                      coupling_scale=1e-6, cutoff=None,
                      apply_qft=True, apply_variational=True,
                      phase_params=None, compress_M=None,
                      eps_regularizer=None):
        """
        One composite step for Absolute Quan level 10:
         - state: complex vector (length N) OR None (will build from C vector if provided)
         - m_vec, f_vec: mass & freq vectors length N (or scalars broadcasted)
         - interaction_matrix: optional NxN
         - returns new normalized state (complex128)
        """
        # determine N
        if state is not None:
            state = np.asarray(state, dtype=np.complex128)
            N = state.shape[0]
        else:
            # if state not provided, require m_vec length to infer N
            if m_vec is not None:
                N = int(np.asarray(m_vec).size)
                state = np.zeros(N, dtype=np.complex128)
            else:
                raise ValueError("state or m_vec (to infer N) must be provided")

        # build energies
        if m_vec is None:
            m_vec = np.zeros(N)
        if f_vec is None:
            f_vec = np.zeros(N)
        Erel = Quan.Erelatif(m_vec)
        Eph = Quan.Efoton(f_vec)

        # build H_eff
        H = Quan.build_H_eff(Erel, Eph, interaction_matrix=interaction_matrix,
                             coupling_scale=coupling_scale, cutoff=cutoff)
        # apply unitary evolution U = exp(i H) (via efficient routine)
        state = Quan.expm_apply(H, state)

        # optional QFT
        if apply_qft:
            state = Quan.qft(state)
        # optional variational layer(s)
        if apply_variational:
            state = Quan.variational_layer(state, phase_params=phase_params)

        # compress amplitudes (prevent exploding range)
        real_part = np.real(state)
        compressed = Quan.compress_array(real_part, M=compress_M)
        # reintroduce phases from state
        phases = np.angle(state)
        state = compressed * np.exp(1j * phases)
        # normalize with adaptive epsilon
        if eps_regularizer is None:
            eps_regularizer = max(1e-12, 1e-12 * (N ** 0.5))
        state = Quan.normalize(state, eps_adaptive=eps_regularizer)
        return state

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Quantum:
    """
    Quantum Infinity (level 10)
    """
    def __init__(self, qubit_size=4, n_cores=2, seed: int | None = None, use_absolute: bool = True):
        self.qubit_size = int(qubit_size)
        self.state = self.initialize()
        self.gates = []
        self.entangled_pairs = []
        self.n_cores = max(1, min(int(n_cores), cpu_count()))
        self._rng = np.random.default_rng(seed)
        self._pool = None
        self.debug_compact = True
        self._damping = 0.995
        self.use_absolute = bool(use_absolute)

        # ensure pool closed on exit
        atexit.register(self.close_pool)

    # === Representation ===
    def initialize(self):
        vec = np.zeros((2 ** self.qubit_size,), dtype=np.complex128)
        vec[0] = 1.0 + 0j
        return vec

    # === Gates ===
    def apply_gate(self, gate, index, adaptive=True):
        I = np.eye(2, dtype=complex)
        ops = [I] * self.qubit_size
        ops[int(index)] = gate
        full_gate = functools.reduce(np.kron, ops)
        if adaptive:
            try:
                abs_mean = float(np.mean(np.abs(self.state)))
                scale = float(np.clip(np.exp(-min(abs_mean, 50.0)), 1e-6, 10.0))
            except Exception:
                scale = 1.0
            full_gate = full_gate * scale
        # apply
        self.state = full_gate @ self.state
        # damping for numeric stability
        self.state *= self._damping
        self.gates.append((gate, int(index)))

    def hadamard(self, index):
        H = (1.0 / math.sqrt(2.0)) * np.array([[1, 1], [1, -1]], dtype=complex)
        self.apply_gate(H, index)

    def pauli_x(self, index):
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        self.apply_gate(X, index)
    def pauli_y(self, index):
        Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        self.apply_gate(Y, index)
    def pauli_z(self, index):
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        self.apply_gate(Z, index)

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

    # === Measurement / summary ===
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
    
    class helpers:
        # === Worker for multiprocessing (uses Quan utilities) ===
        @staticmethod
        def _worker_update_seeded(seed, state_chunk, factor, damping):
            rng = np.random.default_rng(seed)
            chunk = np.ascontiguousarray(state_chunk)
            noise_real = rng.normal(0.0, 0.001 * max(1.0, abs(factor)), size=chunk.shape)
            # keep dtype consistent (complex)
            noise = noise_real.astype(chunk.dtype)
            # use Quan ops for readability: updated = chunk * factor + noise ; then damping
            updated = Quan.kali(chunk, factor)
            updated = Quan.tambah(updated, noise)
            updated = Quan.kali(updated, damping)
            return updated

        # === Multiprocessing update (persistent pool, default max 2 cores) ===
        def unstable_multiprocessing_update(self, factor: float = 1.0):
            if self.state.size == 0:
                return
            if self.state.dtype != np.complex128:
                self.state = self.state.astype(np.complex128)
            self.state = np.ascontiguousarray(self.state)
            n_cores = max(1, min(2, int(self.n_cores)))
            chunks = np.array_split(self.state, n_cores)
            seeds = [int(self._rng.integers(0, 2**31 - 1)) for _ in range(len(chunks))]
            args = [(s, np.ascontiguousarray(c), float(factor), float(self._damping))
                    for s, c in zip(seeds, chunks)]
            if getattr(self, "_pool", None) is None:
                os.environ.setdefault("OMP_NUM_THREADS", "1")
                os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
                os.environ.setdefault("MKL_NUM_THREADS", "1")
                self._pool = Pool(processes=n_cores, maxtasksperchild=200)
            results = self._pool.starmap(Quantum._worker_update_seeded, args)
            self.state = np.concatenate(results)
            norm_val = np.linalg.norm(self.state)
            if norm_val > 0:
                self.state = self.state / norm_val

            # === Helper: memory optimization ===
        def helper_memory(self, enable_trace: bool = True, compress: bool = True):
            """
            Memory helper for Quantum Infinity.
            - enable_trace: aktifkan tracemalloc snapshot (debug)
            - compress: kompres state array agar hemat memory
            """
            # 1. garbage collection
            gc.collect()
            # 2. weakref untuk state snapshot (tidak kunci objek penuh)
            state_ref = weakref.ref(self.state)
            # 3. optional compress (turunkan presisi)
            if compress and self.state is not None:
                # konversi ke float32 untuk hemat ~50% memory
                self.state = self.state.astype(np.complex64)
            # 4. trace memory
            snapshot_info = None
            if enable_trace:
                try:
                    tracemalloc.start()
                    snapshot = tracemalloc.take_snapshot()
                    top_stats = snapshot.statistics("lineno")
                    snapshot_info = [
                        (str(stat.traceback[0]), stat.size / 1024)
                        for stat in top_stats[:5]
                    ]
                    tracemalloc.stop()
                except Exception:
                    snapshot_info = None
            return {
                "state_ref_alive": state_ref() is not None,
                "dtype": str(self.state.dtype),
                "shape": self.state.shape,
                "snapshot": snapshot_info
            }

    # === Absolute-Quan evolution (one-step) ===
    def evolve_absolute(self, m_vec=None, f_vec=None, interaction_matrix=None, coupling_scale=1e-6, cutoff=None,
                        apply_qft=True, apply_variational=True, phase_params=None, compress_M=None, eps_regularizer=None):
        """
        Integrate Absolute Quan step into the Quantum state.
        - Uses Quan.build_H_eff and Quan.expm_apply (which leverages scipy if available).
        - Keeps API optional so older code doesn't need to change.
        """
        N = len(self.state)
        # prepare m_vec / f_vec
        if m_vec is None:
            m_vec = np.zeros(N)
        if f_vec is None:
            f_vec = np.zeros(N)
        Erel = Quan.Erelatif(m_vec)
        Eph = Quan.Efoton(f_vec)

        H = Quan.build_H_eff(Erel, Eph, interaction_matrix=interaction_matrix,
                             coupling_scale=coupling_scale, cutoff=cutoff)
        # apply U = exp(i H)
        try:
            self.state = Quan.expm_apply(H, self.state)
        except Exception:
            # fallback: small perturbation if exp fails
            self.state = self.state * np.exp(1j * np.mean(np.diag(H)))
        if apply_qft:
            self.state = np.fft.fft(self.state) / math.sqrt(len(self.state))
        if apply_variational:
            self.state = Quan.variational_layer(self.state, phase_params=phase_params)

        # compress real amplitudes, then restore phases
        real_part = np.real(self.state)
        compressed = Quan.compress_array(real_part, M=compress_M)
        phases = np.angle(self.state)
        self.state = compressed * np.exp(1j * phases)
        if eps_regularizer is None:
            eps_regularizer = max(1e-12, 1e-12 * (N ** 0.5))
        # normalize
        self.state = Quan.normalize(self.state, eps_adaptive=eps_regularizer)
        return self.state

    # === Algorithms (kept compatible) ===
    def grover(self, oracle_mask_or_fn):
        N = len(self.state)
        if callable(oracle_mask_or_fn):
            mask = oracle_mask_or_fn(self.state)
        else:
            mask = np.asarray(oracle_mask_or_fn, dtype=bool)
        H = (1.0 / math.sqrt(2.0)) * np.array([[1, 1], [1, -1]], dtype=complex)
        for i in range(self.qubit_size):
            self.apply_gate(H, i)
        iterations = int(np.floor(np.pi/4 * math.sqrt(N)))
        for _ in range(iterations):
            self.state[mask] *= -1
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
            # use Absolute update inside VQE loop if available
            if self.use_absolute:
                # small absolute-step as preconditioner
                _ = self.evolve_absolute(coupling_scale=1e-7, apply_qft=False, apply_variational=False)
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

    # === Debug / helper ===
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

    # === Pool management ===
    def close_pool(self):
        if getattr(self, "_pool", None) is not None:
            try:
                self._pool.close()
                self._pool.join()
            except Exception:
                pass
            self._pool = None

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
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    q = Quantum(qubit_size=5, n_cores=2, seed=42, use_absolute=True)
    try:
        q.hadamard(0)
        q.hadamard(1)
        print("Before:", q.compact_summary(top_n=3))
        t0 = time.perf_counter()
        q.unstable_multiprocessing_update(factor=1.0)
        t1 = time.perf_counter()
        print("Multiproc update took", t1 - t0)
        # one Absolute-Quan evolve step (example small mass/freq)
        N = len(q.state)
        m_vec = np.linspace(0.1, 0.5, N)
        f_vec = np.linspace(1e12, 1e13, N)
        q.evolve_absolute(m_vec=m_vec, f_vec=f_vec, coupling_scale=1e-6)
        print("After evolve:", q.compact_summary(top_n=3))
    finally:
        q.close_pool()