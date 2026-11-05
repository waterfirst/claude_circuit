"""PMOS LTPS TFT subcircuit text: symmetric EKV-style B-source with subthreshold slope, W/L-scaled caps and Ioff floor."""

PHI = 0.02585          # thermal voltage at 27 C [V]
SS = 0.15              # subthreshold swing [V/dec]
N = SS / (PHI * 2.302585)  # slope factor so that n*phi*ln10 = SS
KP = 20e-6             # beta per square [A/V^2] (same as previous synthetic card)
COX = 0.30e-15         # gate cap per um^2 [F] (~115 nm SiO2)
LOV = 1.0              # overlap length per side [um]
IOFF_SQ = 1e-12        # off-current floor per square at 1 V [A]
VCAL = 0.15            # model Vth param = extracted |Vth| (10 nA, |Vds| 0.1 V, W/L=1) + VCAL


def subckt(name: str, w: float, l: float, vth_abs: float) -> str:
    """Return a .subckt for one PMOS TFT (ports d g s). vth_abs = |Vth| > 0 (enhancement)."""
    wl = w / l
    vth_abs = vth_abs + VCAL
    k = 2 * N * N * PHI * PHI * KP * wl
    a = 2 * N * PHI
    xf = f"((v(s)-v(g)-{vth_abs:.4f})/{a:.5f})"
    xr = f"((v(d)-v(g)-{vth_abs:.4f})/{a:.5f})"
    sp_f = f"(ln(1+exp(min({xf},40)))+max({xf}-40,0))"   # overflow-safe softplus
    sp_r = f"(ln(1+exp(min({xr},40)))+max({xr}-40,0))"
    cg = COX * w * (l / 2 + LOV)
    roff = 1.0 / (IOFF_SQ * wl)
    return (
        f".subckt {name} d g s\n"
        f"Bch d s I = -{k:.6e}*({sp_f}*{sp_f} - {sp_r}*{sp_r})\n"
        f"Cgs g s {cg:.4e}\nCgd g d {cg:.4e}\nRoff d s {roff:.4e}\n"
        f".ends {name}\n"
    )
