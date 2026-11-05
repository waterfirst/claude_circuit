"""Build one ngspice deck: candidate GIP stage + 5-segment RC gate-line load + clocks/start pulses."""
from ptft import subckt
from topo import CIRCUITS

H = 2.74e-6            # 1H [s]
NH = 3040              # lines per frame
FRAME = NH * H
VGH = 5.8
TR = 30e-9             # clock / pulse edge


def pulse(name, node, td, low_w, per, vgl):
    """Active-low pulse source: VGH idle, VGL for low_w (50 % width)."""
    return f"V{name} {node} 0 PULSE({VGH} {vgl} {td:.6e} {TR:.1e} {TR:.1e} {low_w - TR:.6e} {per:.6e})\n"


def sources(kind, vgl):
    s = f"Vvgh vgh 0 {VGH}\nVvgl vgl 0 {vgl}\n"
    if kind == "scan":
        s += pulse("cka", "cka", 0.13335 * H, 0.7333 * H, 2 * H, vgl)
        s += pulse("ckb", "ckb", 1.13335 * H, 0.7333 * H, 2 * H, vgl)
        s += pulse("stv", "in", 1.08335 * H, 0.8333 * H, FRAME, vgl)
        s += pulse("rst", "rst", 3.08335 * H, 0.8333 * H, FRAME, vgl)
    else:
        s += pulse("si", "si", 1.1 * H, 0.8 * H, FRAME, vgl)
        s += pulse("si1", "si1", 2.1 * H, 0.8 * H, FRAME, vgl)
        s += pulse("esr", "esr", 3000.1 * H, 0.8 * H, FRAME, vgl)
    return s


def load():
    s, prev = "", "out"
    for i in range(1, 6):
        s += f"Rl{i} {prev} l{i} 1.2k\nCl{i} l{i} 0 8p\n"
        prev = f"l{i}"
    return s


def deck(circ, vgl, vth_of, frames=2, tmax=50e-9, outfile="w.dat"):
    """vth_of: function(device_id) -> |Vth| in volts."""
    c = CIRCUITS[circ]
    txt = f"* {circ} VGL={vgl}\n"
    for (dev, d, g, s_, w, l) in c["devs"]:
        txt += subckt(f"p_{dev}", w, l, vth_of(dev))
        txt += f"X{dev} {d} {g} {s_} p_{dev}\n"
    for tag, (a, b, val) in (("C1", c["c1"]), ("C2", c["c2"])):
        txt += f"{tag} {a} {b} {val}\n"
    txt += sources(c["kind"], vgl) + load()
    hold = "v(q) v(qb)" if c["kind"] == "scan" else "v(n1) v(n2)"
    # idle-state initial guess so floating hold nodes start in a defined state
    txt += (f".nodeset v(q)={VGH} v(qb)={vgl + 2.3} v(out)={VGH}\n" if c["kind"] == "scan"
            else f".nodeset v(n1)={VGH} v(n2)={vgl - 3} v(out)={vgl}\n")
    t_end = frames * FRAME
    txt += f".options reltol=1e-3 abstol=1e-12 vntol=1e-5 gmin=1e-15\n"
    txt += f".tran 10n {t_end:.6e} {t_end - FRAME:.6e} {tmax:.1e}\n"
    txt += f".control\nset num_threads=1\nrun\nwrdata {outfile} v(l5) {hold}\nquit\n.endc\n.end\n"
    return txt
