"""Vth states: |Vth| per device. User data: fresh Vth -2.2 ~ -2.4 V, degradation <= 1 V."""

# devices that keep the idle level / bootstrap correct (weakened in M) and that disturb it (strengthened in M)
HOLDERS = {"SCAN7": {"T2", "T6", "T3_1", "T3_2"},
           "SCAN9": {"T2", "T6", "T3", "T7", "T8"},
           "EM8": {"T2", "T6", "T3_1", "T3_2"}}
DISTURB = {"SCAN7": {"T1", "T4", "T5"},
           "SCAN9": {"T1_1", "T1_2", "T4", "T5"},
           "EM8": {"T1", "T4", "T5"}}


def state_fn(state, circ):
    """Return device -> |Vth| function for a named state."""
    if state == "F":     # fresh nominal
        return lambda d: 2.3
    if state == "A05":   # uniform NBTS-direction shift -0.5 V
        return lambda d: 2.8
    if state == "A10":   # worst corner -2.4 V and uniform -1.0 V
        return lambda d: 3.4
    if state == "R10":   # opposite direction worst: -2.2 V shifted +1.0 V
        return lambda d: 1.2
    if state == "M":     # constructed worst mix: holders -1.0 V from -2.4, disturbers +1.0 V from -2.2
        return lambda d: 3.4 if d in HOLDERS[circ] else (1.2 if d in DISTURB[circ] else 2.3)
    raise ValueError(state)


LABEL = {"F": "Fresh −2.3 V", "A05": "열화 −0.5 V (−2.8)", "A10": "열화 −1.0 V 최악 (−3.4)",
         "R10": "역방향 +1.0 V 최악 (−1.2)", "M": "혼합 최악 (홀드 −3.4 / 방해 −1.2)"}
