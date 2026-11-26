# Lab 4 - Task 3
# Empirik Performans və Kolliziya Analizi

import random

TABLE_SIZE = 10007
SEED = 42
NUM_KEYS = 5000


# ------------------------------------------------------------
# 5,000 unikal ISBN generasiya edirik (seed sabitdir → nəticə təkrarlanır)
# ------------------------------------------------------------
def generate_unique_isbns(count=NUM_KEYS, seed=SEED):
    rng = random.Random(seed)
    isbns = set()

    while len(isbns) < count:
        # Realistik 13 rəqəmli format: 978-X-XXXX-XXXX-X
        p1 = rng.randint(0, 9)
        p2 = rng.randint(1000, 9999)
        p3 = rng.randint(1000, 9999)
        p4 = rng.randint(0, 9)
        isbns.add(f"978-{p1}-{p2}-{p3}-{p4}")

    return list(isbns)


# ------------------------------------------------------------
# Polinom hash – a=1 (sadəcə ASCII cəmi) vs a=37 (klassik polinom)
# ------------------------------------------------------------
def poly_hash(key, a, mod_size=TABLE_SIZE):
    h = 0
    for ch in key.replace("-", ""):
        h = (h * a + ord(ch)) % mod_size
    return h


def measure_collisions(keys, a, mod_size=TABLE_SIZE):
    occupied = set()
    collisions = 0

    for k in keys:
        idx = poly_hash(k, a, mod_size)
        if idx in occupied:
            collisions += 1
        else:
            occupied.add(idx)

    return collisions


# ------------------------------------------------------------
# Sabit ölçülü benchmark strukturları.
# Rehash YOXDUR – çünki λ dəyərlərini sabit saxlamaq istəyirik.
# ------------------------------------------------------------
class BenchSeparateChaining:
    def __init__(self, size=TABLE_SIZE):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    def insert(self, key):
        idx = poly_hash(key, 37, self.size)
        self.buckets[idx].append(key)

    def search_probes(self, key):
        idx = poly_hash(key, 37, self.size)
        probes = 0
        for item in self.buckets[idx]:
            probes += 1
            if item == key:
                return probes
        return probes

    def max_chain_length(self):
        return max(len(b) for b in self.buckets)


class BenchOpenAddressing:
    def __init__(self, size=TABLE_SIZE, mode="LINEAR"):
        self.size = size
        self.mode = mode
        self.table = [None] * size

    def _next_step(self, cur, step):
        if self.mode == "LINEAR":
            return (cur + 1) % self.size
        # Quadratic: H(i) = H(i-1) + 2i - 1
        return (cur + 2 * step - 1) % self.size

    def insert(self, key):
        idx = poly_hash(key, 37, self.size)
        for step in range(1, self.size + 1):
            if self.table[idx] is None:
                self.table[idx] = key
                return True
            idx = self._next_step(idx, step)
        return False

    def search_probes(self, key):
        idx = poly_hash(key, 37, self.size)
        probes = 0
        for step in range(1, self.size + 1):
            probes += 1
            if self.table[idx] is None:
                return probes
            if self.table[idx] == key:
                return probes
            idx = self._next_step(idx, step)
        return probes

    def max_cluster_length(self):
        # Ardıcıl dolu xanaların ən uzun parçası
        max_len = cur_len = 0
        for slot in self.table:
            if slot is not None:
                cur_len += 1
                max_len = max(max_len, cur_len)
            else:
                cur_len = 0
        return max_len


# ------------------------------------------------------------
# Eksperimentlər
# ------------------------------------------------------------
def run_experiments():
    keys_5k = generate_unique_isbns(NUM_KEYS, SEED)

    # --- 1) a=1 vs a=37 ---
    col_a1  = measure_collisions(keys_5k, a=1)
    col_a37 = measure_collisions(keys_5k, a=37)

    print("=" * 58)
    print("1. POLİNOM SABİTİ KOLLİZİYA MÜQAYİSƏSİ (5000 ISBN, N=10007)")
    print("=" * 58)
    print(f"  a = 1  (ASCII cəmi)  -> kolliziya: {col_a1}")
    print(f"  a = 37 (polinom hash)-> kolliziya: {col_a37}")

    # --- 2) Maks zəncir / klaster uzunluğu ---
    sc = BenchSeparateChaining(TABLE_SIZE)
    lp = BenchOpenAddressing(TABLE_SIZE, "LINEAR")
    qp = BenchOpenAddressing(TABLE_SIZE, "QUADRATIC")

    for k in keys_5k:
        sc.insert(k)
        lp.insert(k)
        qp.insert(k)

    print("\n" + "=" * 58)
    print("2. MAKS ZƏNCİR / KLASTER UZUNLUĞU (5000 element)")
    print("=" * 58)
    print(f"  Separate Chaining : {sc.max_chain_length()}")
    print(f"  Linear Probing    : {lp.max_cluster_length()}")
    print(f"  Quadratic Probing : {qp.max_cluster_length()}")

    # --- 3) λ dəyərlərinə görə orta probe sayı ---
    # λ=0.90 üçün 9006 element lazımdır, ona görə bir az ehtiyat götürürük.
    keys_all = generate_unique_isbns(int(TABLE_SIZE * 0.90) + 10, SEED)
    lambdas = [0.25, 0.50, 0.75, 0.90]

    print("\n" + "=" * 58)
    print("3. MÜXTƏLİF λ ÜÇÜN ORTA AXTARIŞ ADDIMI")
    print("=" * 58)
    print(f"{'λ':<10}| {'Sep.Chain':<12}| {'Linear':<12}| {'Quadratic':<12}")
    print("-" * 50)

    for lam in lambdas:
        n = int(TABLE_SIZE * lam)
        subset = keys_all[:n]

        sc = BenchSeparateChaining(TABLE_SIZE)
        lp = BenchOpenAddressing(TABLE_SIZE, "LINEAR")
        qp = BenchOpenAddressing(TABLE_SIZE, "QUADRATIC")

        for k in subset:
            sc.insert(k)
            lp.insert(k)
            qp.insert(k)

        avg_sc = sum(sc.search_probes(k) for k in subset) / n
        avg_lp = sum(lp.search_probes(k) for k in subset) / n
        avg_qp = sum(qp.search_probes(k) for k in subset) / n

        print(f"{lam:<10.2f}| {avg_sc:<12.3f}| {avg_lp:<12.3f}| {avg_qp:<12.3f}")


if __name__ == "__main__":
    run_experiments()
