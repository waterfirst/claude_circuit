"""Figures for the VGL sweep report: pass map and waveforms (matplotlib, PNG)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gen import H
from states import LABEL

CIRC_NAME = {"SCAN7": "GI/GC (SCAN7)", "SCAN9": "GW (SCAN9)", "EM8": "EM/GB (EM8)"}
PASS_C, FAIL_C = "#1e7b4a", "#b3261e"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})


def pass_map(res, circs, states, vgls, path):
    """Grid: rows = circuit x state, cols = VGL; green pass / red fail."""
    rows = [(c, s) for c in circs for s in states]
    fig, ax = plt.subplots(figsize=(9, 0.32 * len(rows) + 1.2))
    for i, (c, s) in enumerate(rows):
        for j, v in enumerate(vgls):
            r = res.get((c, s, v))
            col = "#999999" if r is None else (PASS_C if r["ok"] else FAIL_C)
            ax.add_patch(plt.Rectangle((j, i), 0.92, 0.85, color=col))
    ax.set_xlim(0, len(vgls)); ax.set_ylim(len(rows), 0)
    ax.set_xticks(np.arange(len(vgls)) + 0.46, [f"{v:g}" for v in vgls])
    ax.set_yticks(np.arange(len(rows)) + 0.42, [f"{CIRC_NAME[c]} · {s}" for c, s in rows])
    ax.set_xlabel("VGL (V)   ■ green = pass, red = fail")
    ax.tick_params(length=0); [sp.set_visible(False) for sp in ax.spines.values()]
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def waves(wdir, circ, states, vgls, path):
    """Far-end output around the active pulse (0-8H) for each state; one panel per VGL."""
    fig, axs = plt.subplots(1, len(vgls), figsize=(10, 3.0), sharey=True)
    for ax, v in zip(axs, vgls):
        for s in states:
            f = os.path.join(wdir, f"{circ}_{s}_{v:+.1f}_100ns.npy")
            if not os.path.exists(f):
                continue
            a = np.load(f); m = a[:, 0] < 6 * H
            ax.plot(a[m, 0] / H, a[m, 1], lw=1.2, label=s)
        ax.set_title(f"VGL {v:g} V"); ax.set_xlabel("t (H)"); ax.grid(alpha=.25)
    axs[0].set_ylabel("far-end out (V)")
    axs[-1].legend(fontsize=7, frameon=False)
    fig.suptitle(CIRC_NAME[circ], x=0.01, ha="left", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
