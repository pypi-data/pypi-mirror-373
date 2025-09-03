import numpy as np
import stumpy
from scipy.spatial.distance import cdist
import time


def benchmark_stumpy(ts, m):
    start = time.time()
    mp = stumpy.gpu_stump(ts, m)
    elapsed = time.time() - start
    return elapsed, mp



def benchmark_cdist(ts, m):
    start = time.time()

    # Extract subsequences
    n = len(ts)
    k = n - m + 1
    X = np.lib.stride_tricks.sliding_window_view(ts, window_shape=m)

    # Z-normalize each subsequence
    X = (X - X.mean(axis=1, keepdims=True)) / X.std(axis=1, keepdims=True)

    # Compute pairwise correlation distance (1 - Pearson r)
    D = cdist(X, X, metric='correlation')

    elapsed = time.time() - start
    return elapsed



for size in [1000]:
    ts = np.random.rand(size)
    m = 50

    t_stumpy, r = benchmark_stumpy(ts, m)
    #t_cdist = benchmark_cdist(ts, m)

    print(f"\nTime series length: {size}")
    print(f"STUMPY     : {t_stumpy:.4f} sec")
    #print(f"CDIST brute: {t_cdist:.4f} sec")