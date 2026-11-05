"""Assemble report.html (tables + figures) from results*.jsonl; prose comes from summary.html / notes.html."""
import base64, json, os
from figs import pass_map, waves, CIRC_NAME
from run import VGLS, STATES
from states import LABEL

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, "figs")


def load(name):
    p = os.path.join(ROOT, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def img(path, alt):
    b = base64.b64encode(open(path, "rb").read()).decode()
    return f"<figure><img alt='{alt}' src='data:image/png;base64,{b}'><figcaption>{alt}</figcaption></figure>"


def margin(res, c, s):
    """Least-negative VGL reached by continuous passing from -9 V upward."""
    best = None
    for v in sorted(VGLS):
        r = res.get((c, s, v))
        if not r or not r["ok"]:
            break
        best = v
    return best


def build():
    os.makedirs(FIG, exist_ok=True)
    rows = load("results.jsonl"); res = {(r["circ"], r["state"], r["vgl"]): r for r in rows}
    circs = ["SCAN7", "SCAN9", "EM8"]
    pass_map(res, circs, STATES, sorted(VGLS), os.path.join(FIG, "pass_map.png"))
    for c in circs:
        waves(os.path.join(ROOT, "waves"), c, STATES, [-9.0, -6.0, -3.0], os.path.join(FIG, f"wave_{c}.png"))
    t = "<div class='tw'><table><tr><th>회로</th><th>상태</th><th>연속 통과 최고 VGL</th><th>−9 V 대비 여유</th><th>첫 실패 VGL</th><th>첫 실패 사유</th></tr>"
    for c in circs:
        for s in STATES:
            m = margin(res, c, s)
            fails = sorted([r for r in rows if r["circ"] == c and r["state"] == s and not r["ok"]], key=lambda r: r["vgl"])
            f = fails[0] if fails else None
            ok = m is not None and m >= -3.0
            t += (f"<tr><td>{CIRC_NAME[c]}</td><td>{LABEL[s]}</td><td class='{'pass' if ok else 'fail'}'>"
                  f"{'-' if m is None else f'{m:g} V'}</td><td>{'-' if m is None else f'{m + 9:.1f} V'}</td>"
                  f"<td>{f['vgl'] if f else '-'}</td><td>{f['why'] if f else '전 구간 통과'}</td></tr>")
    t += "</table></div>"
    d = "<div class='tw'><table><tr><th>회로</th><th>상태</th><th>VGL</th><th>active</th><th>idle</th><th>지연 ns</th><th>폭 ns</th><th>리플</th><th>홀드 노드 idle</th><th>부트스트랩 최저</th><th>판정</th></tr>"
    for r in sorted(rows, key=lambda r: (circs.index(r["circ"]), STATES.index(r["state"]), r["vgl"])):
        if r["vgl"] not in (-9.0, -7.0, -5.0, -3.0) or "active" not in r:
            continue
        d += (f"<tr><td>{CIRC_NAME[r['circ']]}</td><td>{r['state']}</td><td>{r['vgl']:g}</td><td>{r['active']:.2f}</td>"
              f"<td>{r['idle']:.2f}</td><td>{r['delay_ns']:.0f}</td><td>{r['width_ns']:.0f}</td><td>{r['ripple']:.3f}</td>"
              f"<td>{r['hold_idle']:.2f}</td><td>{r['boot_min']:.1f}</td><td class='{'pass' if r['ok'] else 'fail'}'>"
              f"{'PASS' if r['ok'] else 'FAIL'}</td></tr>")
    d += "</table></div>"
    half = load("results_tmax_half.jsonl"); hv = ""
    if half:
        hv = "<div class='tw'><table><tr><th>회로</th><th>상태</th><th>지연 변화 %</th><th>폭 변화 %</th><th>active 차 V</th><th>판정 일치</th></tr>"
        for h in sorted(half, key=lambda r: (circs.index(r["circ"]), STATES.index(r["state"]))):
            b = res.get((h["circ"], h["state"], -9.0))
            if not b or "active" not in h or "active" not in b:
                continue
            pct = lambda k: abs(h[k] - b[k]) / abs(b[k]) * 100 if b[k] else 0
            hv += (f"<tr><td>{CIRC_NAME[h['circ']]}</td><td>{h['state']}</td><td>{pct('delay_ns'):.2f}</td>"
                   f"<td>{pct('width_ns'):.2f}</td><td>{abs(h['active'] - b['active']):.3f}</td>"
                   f"<td>{'Y' if h['ok'] == b['ok'] else 'N'}</td></tr>")
        hv += "</table></div>"
    figs = img(os.path.join(FIG, "pass_map.png"), "VGL 통과 지도 (초록 통과, 빨강 실패)")
    figs += "".join(img(os.path.join(FIG, f"wave_{c}.png"), f"{CIRC_NAME[c]} 원단 출력 파형 (0~6H)") for c in circs)
    part = lambda n: open(os.path.join(ROOT, n)).read() if os.path.exists(os.path.join(ROOT, n)) else ""
    html = (part("head.html") + part("summary.html") + "<h2>3. VGL별 여유</h2>" + t + "<h2>4. 그림</h2>" + figs
            + "<h2>5. 상세 지표 (VGL −9 / −7 / −5 / −3 V)</h2>" + d + "<h2>6. 수치 검증 (tmax 100 → 50 ns, VGL −9 V)</h2>"
            + hv + part("notes.html") + "</main>\n")
    open(os.path.join(ROOT, "report.html"), "w").write(html)
    return len(rows), len(half)


if __name__ == "__main__":
    print(build())
