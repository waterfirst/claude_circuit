# claude_circuit

ngspice simulations of OLED GIP (gate-in-panel) driver candidate circuits.

## gip_vgl_sweep — VGL −3 ~ −9 V sweep (2026-11-06)

Candidate LTPS-PMOS GIP stages (topologies based on public patents, not a product netlist)
simulated with a substitute TFT model at realistic Vth (−2.2 ~ −2.4 V) and degradation ≤ 1 V.

| Circuit | Drivers | Result (VGL −9 → −3 V) |
|---|---|---|
| SCAN7 | GI / GC | all 5 Vth states pass down to −3 V |
| SCAN9 | GW | all 5 Vth states pass down to −3 V |
| EM8 | EM / GB | pass to −3 V except constructed worst mix (M): fails at −3 V (width +38 %), passes at −3.5 V |

Main finding: with |Vth| ≥ 2 V, leakage failures seen with the earlier low-Vth synthetic card disappear;
the remaining limit is threshold loss slowing the EM/GB falling edge at shallow VGL.

Open `gip_vgl_sweep/report.html` for tables, pass map and waveforms (Korean).

### Files
| File | Role |
|---|---|
| `ptft.py` | PMOS TFT subcircuit (symmetric EKV-style B-source, SS 0.15 V/dec, Vth calibrated at 10 nA) |
| `topo.py` | Candidate node tables (SCAN7, SCAN9, EM8) |
| `gen.py` | Deck builder: sources, clocks, 5-segment RC load (6 kΩ / 40 pF) |
| `states.py` | Vth states F / A05 / A10 / R10 / M |
| `judge.py` | Pass/fail metrics on the last-frame far-end waveform |
| `run.py` | Parallel sweep runner (`main` = 195 runs, `half` = tmax/2 check) |
| `figs.py`, `report.py` | Figures and HTML report |
| `results*.jsonl` | Per-run metrics |
| `waves/*.npy` | Downsampled waveforms (VGL −9/−6/−3 V) |
| `idvg.cir` | Single-device Id-Vg check deck |

### Reproduce
```bash
cd gip_vgl_sweep
python3 run.py main && python3 run.py half && python3 report.py
```
Requires ngspice ≥ 42, Python 3 with numpy and matplotlib.

### Limits
Assumed topology, substitute model (not the measured card), uniform/constructed ΔVth instead of the
per-device table, 27 °C, single stage. Trend check only — not a product margin.
