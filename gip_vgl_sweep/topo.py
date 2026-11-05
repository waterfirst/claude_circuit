"""Candidate GIP topologies copied from the 2026-10-15 report node tables (ID, drain, gate, source, W, L)."""

SCAN7 = [  # GI, GC
    ("T1", "q", "ckb", "in", 3.9, 4), ("T2", "qb", "ckb", "vgl", 3.9, 4),
    ("T3_1", "x", "qb", "vgh", 4.22, 4.5), ("T3_2", "q", "cka", "x", 4.22, 4.5),
    ("T4", "qb", "q", "vgh", 3.9, 4), ("T5", "out", "q", "cka", 96, 4),
    ("T6", "out", "qb", "vgh", 64, 4),
]
SCAN9 = [  # GW
    ("T1_1", "y", "ckb", "in", 4.22, 4.5), ("T1_2", "q", "ckb", "y", 4.22, 4.5),
    ("T2", "qb", "ckb", "vgl", 3.9, 4), ("T3", "x", "qb", "vgh", 3.9, 4),
    ("T7", "q", "cka", "x", 3.9, 4), ("T4", "qb", "q", "vgh", 3.9, 4),
    ("T5", "out", "q", "cka", 120, 4), ("T6", "out", "qb", "vgh", 40, 4),
    ("T8", "q", "rst", "vgh", 3.9, 4),
]
EM8 = [  # EM, GB
    ("T1", "n1", "si", "vgl", 3.9, 4), ("T2", "out", "n2", "vgl", 320, 4),
    ("T3_1", "z", "n2", "vgh", 4.22, 4.5), ("T3_2", "n1", "n2", "z", 4.22, 4.5),
    ("T4", "n2", "si", "vgh", 3.9, 4), ("T5", "out", "n1", "vgh", 180, 4),
    ("T6", "n2", "si1", "vgl", 3.9, 4), ("T7", "n1", "esr", "vgh", 3.9, 4),
]

# kind: scan = active-low output pulse, em = active-high output pulse
CIRCUITS = {
    "SCAN7": dict(devs=SCAN7, kind="scan", c1=("q", "out", 1.0e-12), c2=("qb", "vgh", 0.3e-12)),
    "SCAN9": dict(devs=SCAN9, kind="scan", c1=("q", "out", 1.0e-12), c2=("qb", "vgh", 0.3e-12)),
    "EM8": dict(devs=EM8, kind="em", c1=("n2", "out", 4.0e-12), c2=("n1", "vgh", 0.3e-12)),
}
DRIVERS = {"GI/GC": "SCAN7", "GW": "SCAN9", "EM/GB": "EM8"}
