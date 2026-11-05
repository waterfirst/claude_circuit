"""Pass/fail metrics for one last-frame far-end waveform (same criteria as the 2026-10-15 report)."""
import numpy as np
from gen import H, FRAME, VGH

SPEC = {  # ref edge (50 %), expected active window, expected width
    "scan": dict(ref=2.13335 * H, win=(2.13335 * H, 2.86665 * H), width=0.7333 * H),
    "em": dict(ref=1.1 * H, win=(1.1 * H, 2.1 * H), width=1.0 * H),
}


def judge(kind, t, out, vgl):
    """t is time inside the last frame (0..FRAME). Returns dict of metrics + verdict."""
    sp, span = SPEC[kind], VGH - vgl
    act_t, idle_t = (vgl, VGH) if kind == "scan" else (VGH, vgl)
    a0, a1 = sp["win"]
    q = (a1 - a0) / 4
    act = float(np.median(out[(t > a0 + q) & (t < a1 - q)]))
    im = (t > 6 * H) & (t < FRAME - 2 * H)
    idle = float(np.median(out[im]))
    ripple = float((out[im].max() - out[im].min()) / span)
    mid = (VGH + vgl) / 2
    s = np.sign(out - mid)
    xi = np.where(np.diff(s) != 0)[0]
    xt = t[xi]
    pulses = len(xt) / 2
    delay = float(xt[0] - sp["ref"]) if len(xt) else float("nan")
    width = float(xt[1] - xt[0]) if len(xt) >= 2 else float("nan")
    reasons = []
    if abs(act - act_t) > 0.05 * span: reasons.append(f"active {act:.2f}V")
    if abs(idle - idle_t) > 0.05 * span: reasons.append(f"idle {idle:.2f}V")
    if not (delay < 0.5 * H): reasons.append(f"delay {delay*1e9:.0f}ns")
    if not (abs(width / sp["width"] - 1) <= 0.35): reasons.append(f"width {width*1e9:.0f}ns")
    if ripple >= 0.2: reasons.append(f"ripple {ripple:.2f}")
    if pulses != 1: reasons.append(f"pulses {pulses:g}")
    return dict(active=act, idle=idle, ripple=ripple, pulses=pulses, delay_ns=delay * 1e9,
                width_ns=width * 1e9, ok=not reasons, why="; ".join(reasons))
