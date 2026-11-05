"""Run the VGL sweep in parallel; write results.jsonl and keep downsampled waveforms for plotting."""
import json, os, subprocess, sys, itertools
from multiprocessing import Pool
import numpy as np
from gen import deck, FRAME, H
from judge import judge
from states import state_fn
from topo import CIRCUITS

ROOT = os.path.dirname(os.path.abspath(__file__))
VGLS = [round(-9.0 + 0.5 * i, 1) for i in range(13)]       # -9.0 .. -3.0
STATES = ["F", "A05", "A10", "R10", "M"]
KEEP_WAVE = {-9.0, -6.0, -3.0}


def one(job):
    circ, st, vgl, tmax = job
    tag = f"{circ}_{st}_{vgl:+.1f}_{tmax*1e9:.0f}ns"
    wd = os.path.join(ROOT, "runs", tag)
    os.makedirs(wd, exist_ok=True)
    open(os.path.join(wd, "d.cir"), "w").write(deck(circ, vgl, state_fn(st, circ), tmax=tmax))
    r = subprocess.run(["ngspice", "-b", "d.cir"], cwd=wd, capture_output=True, text=True, timeout=900)
    res = dict(circ=circ, state=st, vgl=vgl, tmax_ns=tmax * 1e9)
    try:
        a = np.loadtxt(os.path.join(wd, "w.dat"))
    except Exception as e:  # simulation failure is recorded, not hidden
        res.update(ok=False, why=f"SIM_FAIL {e}", finite=False, log=r.stdout[-300:])
        return res
    t = a[:, 0] - (a[-1, 0] - FRAME)
    out, h1, h2 = a[:, 1], a[:, 3], a[:, 5]
    res.update(judge(CIRCUITS[circ]["kind"], t, out, vgl))
    res["finite"] = bool(np.isfinite(a).all())
    res["hold_idle"] = float(np.median(h2[(t > 6 * H) & (t < FRAME - 2 * H)]))
    res["boot_min"] = float(h1.min()) if CIRCUITS[circ]["kind"] == "scan" else float(h2.min())
    if vgl in KEEP_WAVE and tmax == 100e-9:
        m = t < 8 * H
        idx = np.concatenate([np.where(m)[0], np.where(~m)[0][::200]])
        np.save(os.path.join(ROOT, "waves", tag + ".npy"), np.c_[t[idx], out[idx], h1[idx], h2[idx]])
    os.remove(os.path.join(wd, "w.dat"))
    return res


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "waves"), exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "main"
    if mode == "main":
        jobs = [(c, s, v, 100e-9) for c, s, v in itertools.product(CIRCUITS, STATES, VGLS)]
        outf = "results.jsonl"
    else:  # tmax/2 numerical check at VGL -9 V
        jobs = [(c, s, -9.0, 50e-9) for c, s in itertools.product(CIRCUITS, STATES)]
        outf = "results_tmax_half.jsonl"
    with Pool(2) as p, open(os.path.join(ROOT, outf), "w") as f:
        for i, res in enumerate(p.imap_unordered(one, jobs), 1):
            f.write(json.dumps(res) + "\n"); f.flush()
            print(i, len(jobs), res["circ"], res["state"], res["vgl"], res["ok"], res.get("why", ""), flush=True)
