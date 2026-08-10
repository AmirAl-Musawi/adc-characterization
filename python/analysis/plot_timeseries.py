import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR = "docs"
WINDOW = 64

CAPTURES = [
    ("data/example_variable_interval.csv", "near_boundary"),
    ("data/example_noise_1k.csv", "drifted"),
]


def read_capture(path):
    stamp = "unknown time"
    n_header = 0

    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                break
            n_header += 1
            if line.startswith("# date:"):
                stamp = line.split(":", 1)[1].strip()

    n_header += 1                # the column header row

    data = np.genfromtxt(path, delimiter=",", skip_header=n_header)
    return data[:, 0], data[:, 2], stamp


def plot_capture(path, tag):
    index, raw, stamp = read_capture(path)

    codes = np.unique(raw)
    frac_low = np.count_nonzero(raw == codes.min()) / raw.size

    print(f"{path}")
    print(f"  {raw.size} samples, recorded {stamp}")
    print(f"  mean {raw.mean():.4f} LSB, sigma {raw.std():.4f} LSB")
    print(f"  codes {codes.astype(int)}, {frac_low:.1%} at code {int(codes.min())}")

    # --- figure 1: raw time series
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(index, raw, marker=".", linestyle="none", markersize=2,
            color="#1f77b4")

    ax.set_yticks(codes)
    ax.set_ylim(codes.min() - 0.2, codes.max() + 0.2)

    ax.set_xlabel("Sample index")
    ax.set_ylabel("ADC code [LSB]")
    ax.set_title(f"ADC output at the 511/512 code boundary — {stamp}")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/timeseries_{tag}.png", dpi=150)
    plt.close(fig)

    # --- figure 2: dither

    kernel = np.ones(WINDOW) / WINDOW
    moving_avg = np.convolve(raw, kernel, mode="valid")
    index_ma = index[WINDOW - 1:]

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax_top.plot(index, raw, marker=".", linestyle="none", markersize=2,
                alpha=0.25, color="#1f77b4", label="raw samples")
    ax_top.plot(index_ma, moving_avg, linewidth=1.5, color="#d62728",
                label=f"moving average, N = {WINDOW}")
    ax_top.set_yticks(codes)
    ax_top.set_ylim(codes.min() - 0.2, codes.max() + 0.2)
    ax_top.set_ylabel("ADC code [LSB]")
    ax_top.set_title(f"Averaging recovers a value between two adjacent ADC "
                     f"codes — {stamp}")
    ax_top.grid(True, alpha=0.3)
    ax_top.legend(loc="lower right")

    ax_bot.plot(index_ma, moving_avg, linewidth=1.5, color="#d62728")
    ax_bot.axhline(raw.mean(), color="black", linestyle="--", linewidth=0.8,
                   label=f"overall mean = {raw.mean():.4f} LSB")
    ax_bot.ticklabel_format(axis="y", useOffset=False, style="plain")
    ax_bot.set_xlabel("Sample index")
    ax_bot.set_ylabel("ADC code [LSB]")
    ax_bot.set_title("Same curve, vertical zoom — the steps are 1/N = "
                     f"{1 / WINDOW:.4f} LSB")
    ax_bot.grid(True, alpha=0.3)
    ax_bot.legend(loc="lower right")

    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/dither_{tag}.png", dpi=150)
    plt.close(fig)

    print(f"  moving average spans {moving_avg.min():.4f} to "
          f"{moving_avg.max():.4f} LSB")
    print(f"  wrote {OUTDIR}/timeseries_{tag}.png and {OUTDIR}/dither_{tag}.png")


os.makedirs(OUTDIR, exist_ok=True)

for csv_path, tag in CAPTURES:
    plot_capture(csv_path, tag)