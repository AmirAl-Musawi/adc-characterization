import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "data/main_17min.csv"
OUTDIR = "docs"

BLOCK_SIZES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
               1024, 2048, 4096, 8192, 16384]

ACF_SAMPLES = 50000     # segment used for the autocorrelation
ACF_MAX_LAG = 200       # lags to evaluate, ~0.26 s at 1276.7 us
MAINS_HZ = 50.0

with open(CSV) as f:
    n_header = sum(1 for line in f if line.startswith("#")) + 1

print(f"loading {CSV} ...")
t_us, raw = np.loadtxt(CSV, delimiter=",", skiprows=n_header,
                       usecols=(1, 2), unpack=True)

n = raw.size
interval_us = (t_us[-1] - t_us[0]) / (n - 1)
sigma1 = raw.std()

print(f"{n} samples, mean interval {interval_us:.1f} us, "
      f"duration {(t_us[-1] - t_us[0]) / 1e6:.1f} s")
print(f"mean {raw.mean():.4f} LSB, sigma {sigma1:.4f} LSB")

os.makedirs(OUTDIR, exist_ok=True)


# --- averaging law

print("\nN        blocks   sigma_meas   sigma_theory   ratio   +/-")

sizes, measured, theory = [], [], []
limit_n = None

for N in BLOCK_SIZES:
    n_blocks = n // N
    if n_blocks < 30:
        break
    block_means = raw[:n_blocks * N].reshape(-1, N).mean(axis=1)

    sigma_n = block_means.std()
    sigma_theory = sigma1 / np.sqrt(N)
    ratio = sigma_n / sigma_theory

    unc = 1.0 / np.sqrt(2.0 * (n_blocks - 1))

    sizes.append(N)
    measured.append(sigma_n)
    theory.append(sigma_theory)

    if abs(ratio - 1.0) <= max(3.0 * unc, 0.10):
        limit_n = N

    print(f"{N:<8} {n_blocks:<8} {sigma_n:<12.6f} {sigma_theory:<14.6f} "
          f"{ratio:<7.3f} {unc:.1%}")

print(f"\n1/sqrt(N) holds up to N = {limit_n}")
print(f"that is {limit_n * interval_us / 1e6:.2f} s of averaging")

fig, ax = plt.subplots(figsize=(7, 5))
ax.loglog(sizes, theory, linestyle="--", color="black", linewidth=1,
          label=r"theory, $\sigma_1/\sqrt{N}$")
ax.loglog(sizes, measured, marker="o", markersize=5, linestyle="none",
          color="#d62728", label="measured")
ax.set_xlabel("Block size N [samples]")
ax.set_ylabel(r"$\sigma$ of block means [LSB]")
ax.set_title("Averaging law: does the noise fall as $1/\\sqrt{N}$?")
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(f"{OUTDIR}/sqrt_n_law.png", dpi=150)
plt.close(fig)


# --- autocorrelation

seg = raw[:ACF_SAMPLES] - raw[:ACF_SAMPLES].mean()
denom = np.dot(seg, seg)

lags = np.arange(ACF_MAX_LAG + 1)
acf = np.array([np.dot(seg[:seg.size - k], seg[k:]) / denom for k in lags])

band = 1.96 / np.sqrt(seg.size)

mains_period = (1e6 / MAINS_HZ) / interval_us
print(f"\nautocorrelation over {ACF_SAMPLES} samples, lags 0..{ACF_MAX_LAG}")
print(f"a {MAINS_HZ:.0f} Hz disturbance would appear with a period of "
      f"{mains_period:.2f} samples")
print(f"acf[1] = {acf[1]:.4f}, significance band +/- {band:.4f}")
strong = [int(k) for k in lags[1:] if abs(acf[k]) > band]
print(f"lags outside the band: {strong[:20]}{' ...' if len(strong) > 20 else ''}")

fig, ax = plt.subplots(figsize=(10, 4))
ax.axhline(0, color="black", linewidth=0.8)
ax.axhspan(-band, band, color="grey", alpha=0.25,
           label=f"95 % band for uncorrelated data")

for m in range(1, int(ACF_MAX_LAG / mains_period) + 1):
    ax.axvline(m * mains_period, color="#1f77b4", linestyle=":", linewidth=0.8,
               label=f"multiples of {MAINS_HZ:.0f} Hz period" if m == 1 else None)

ax.plot(lags, acf, marker=".", markersize=3, linewidth=1, color="#d62728",
        label="autocorrelation")
ax.set_xlabel("Lag [samples]")
ax.set_ylabel("Normalised autocorrelation")
ax.set_title(f"Are successive samples independent? "
             f"({interval_us:.1f} us between samples)")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig(f"{OUTDIR}/autocorrelation.png", dpi=150)
plt.close(fig)

print(f"\nwrote {OUTDIR}/sqrt_n_law.png and {OUTDIR}/autocorrelation.png")