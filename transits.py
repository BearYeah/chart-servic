"""Vedic transits (Gochara) for the reading window: this project's addition.

The package template lists the Vimshottari periods but no transit positions,
so a reading could not check a dasha window against Jupiter and Saturn. This
module computes, with the same Swiss Ephemeris (built-in Moshier), sidereal
mode and lock as the verbatim engine, the sign segments of Jupiter, Saturn,
Rahu and Ketu from the as-of date over the forecast window, and the houses
both Jupiter and Saturn reach at once (double transit), counted from the
natal Lagna and from the natal Moon.

Whole-sign houses; Parasara aspects only (Jupiter 5/7/9, Saturn 3/7/10, and
every planet its own sign). Day steps: ingress dates are accurate to a day,
which the text says. Nothing here interprets the result.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import charts

BODIES = (("Jupiter", "木星"), ("Saturn", "土星"), ("Rahu", "罗睺"))
ASPECTS = {"Jupiter": (1, 5, 7, 9), "Saturn": (1, 3, 7, 10)}


def _house(sign: int, base: int) -> int:
    return (sign - base) % 12 + 1


def _segments(chart_input: dict, start: datetime, days: int) -> dict[str, list[dict]]:
    import swisseph as swe
    modes = {"lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN, "krishnamurti": swe.SIDM_KRISHNAMURTI}
    ids = {"Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
           "Rahu": swe.TRUE_NODE if chart_input.get("node_type") == "true" else swe.MEAN_NODE}
    flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out: dict[str, list[dict]] = {key: [] for key, _ in BODIES}
    with charts._SWE_LOCK:
        swe.set_sid_mode(modes[chart_input.get("ayanamsa", "lahiri")])
        for day in range(days + 1):
            moment = start + timedelta(days=day)
            utc = moment.astimezone(timezone.utc)
            jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60)
            for key, _ in BODIES:
                coords, _ = swe.calc_ut(jd, ids[key], flags)
                sign, retro = int((coords[0] % 360) / 30), coords[3] < 0
                rows = out[key]
                # Nodes always move backwards; only their sign changes matter.
                state = (sign, retro if key != "Rahu" else True)
                if rows and (rows[-1]["sign"], rows[-1]["retrograde"]) == state:
                    rows[-1]["end"] = moment
                else:
                    rows.append({"sign": sign, "retrograde": state[1], "start": moment, "end": moment})
    out["Ketu"] = [{**row, "sign": (row["sign"] + 6) % 12} for row in out["Rahu"]]
    return out


def _reach(key: str, sign: int) -> set[int]:
    return {(sign + n - 1) % 12 for n in ASPECTS[key]}


def compute(chart: dict) -> dict:
    value = chart["input"]
    vedic = chart["vedic"]
    tz = timezone(timedelta(hours=value["utc_offset"]))
    start = datetime.fromisoformat(value["as_of_date"]).replace(tzinfo=tz)
    days = int(value.get("forecast_years", 5) * 365.25)
    lagna = vedic["ascendant"]["longitude"] // 30
    moon = next(p for p in vedic["planets"] if p["key"] == "Moon")["sign_index"]
    segments = _segments(value, start, days)
    # Double transit: periods where Jupiter and Saturn both reach the same sign.
    double = []
    for j in segments["Jupiter"]:
        for s in segments["Saturn"]:
            lo, hi = max(j["start"], s["start"]), min(j["end"], s["end"])
            if lo > hi:
                continue
            shared = sorted(_reach("Jupiter", j["sign"]) & _reach("Saturn", s["sign"]))
            if double and double[-1]["signs"] == shared and (lo - double[-1]["end"]).days <= 1:
                double[-1]["end"] = hi
            else:
                double.append({"start": lo, "end": hi, "signs": shared})
    return {"start": start, "days": days, "lagna": int(lagna), "moon": int(moon),
            "segments": segments, "double": double}


def _date(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d")


def template_section(chart: dict) -> str:
    t = compute(chart)
    signs, lagna, moon = charts.SIGNS, t["lagna"], t["moon"]
    names = dict(BODIES) | {"Ketu": "计都"}
    lines = ["", "## 行运 Gochara（本地计算，供双重行运验证）",
             f"- 口径：与本命盘相同的恒星黄道与岁差；整宫制；自基准日 {_date(t['start'])} 起约 {t['days'] // 365} 年；"
             "逐日采样，进出星座与顺逆转换的日期精确到天。宫位同时给出“自上升”与“自月亮”两种起算。",
             f"- 本命上升：{signs[lagna]}；本命月亮：{signs[moon]}。",
             "- 相位按 Parasara：木星照第 5、7、9 宫，土星照第 3、7、10 宫，均含所在宫本身。行运不等于现实事件。"]
    for key in ("Jupiter", "Saturn", "Rahu", "Ketu"):
        lines.append(f"### 行运{names[key]}")
        for row in t["segments"][key]:
            motion = "" if key in ("Rahu", "Ketu") else ("逆行" if row["retrograde"] else "顺行")
            lines.append(f"- {_date(row['start'])} 至 {_date(row['end'])}：{signs[row['sign']]}"
                         f"{('，' + motion) if motion else ''}；自上升第 {_house(row['sign'], lagna)} 宫，"
                         f"自月亮第 {_house(row['sign'], moon)} 宫。")
    lines.append("### 木土双重行运（两星同时落入或照到的星座）")
    for row in t["double"]:
        if not row["signs"]:
            continue
        parts = "、".join(f"{signs[s]}（自上升第 {_house(s, lagna)} 宫／自月亮第 {_house(s, moon)} 宫）" for s in row["signs"])
        lines.append(f"- {_date(row['start'])} 至 {_date(row['end'])}：{parts}")
    lines.append("- 边界：只列木星、土星与南北交点；内行星行运、Ashtakavarga 分数与 Sade Sati 细分未计算。")
    return "\n".join(lines) + "\n"
