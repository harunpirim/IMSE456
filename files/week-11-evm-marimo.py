# /// script
# requires-python = ">=3.10"
# dependencies = ["marimo", "altair", "pandas"]
# ///
"""Week 11 · Earned value, interactively: the chapter's Digital Camera project and the conference.

IMSE 456/656 · Larson & Gray, Chapter 13. Open in the browser, nothing to install:
https://marimo.app/github.com/harunpirim/IMSE456/blob/main/files/week-11-evm-marimo.py
"""

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Week 11 · Earned value")


@app.cell(hide_code=True)
def _():
    from datetime import date, timedelta

    import altair as alt
    import marimo as mo
    import pandas as pd
    return alt, date, mo, pd, timedelta


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 11 · Earned value, interactively

    IMSE 456/656 · Program and Project Management · Larson & Gray, Chapter 13

    This notebook checks Tuesday's worksheet and lets you change a status report to see what every earned value measure does. Pick a project and a status report below, then work down the page:

    1. **The baseline.** The time-phased budget, PV, that every report is measured against.
    2. **The status report.** Percent complete and actual cost for each activity; EV, the variances, the indexes and the forecasts. Answers stay hidden until you switch them on, so you can fill in the worksheet first.
    3. **The graphs.** The cost/schedule graph and the index trend, with your report on them.
    4. **The schedule.** What the network says about the finish, which the dollars do not.

    Everything recalculates as you move a control; there is nothing to run.
    """)
    return


@app.cell(hide_code=True)
def _():
    EXAMPLES = {
        "The conference (weekly status reports)": dict(
            unit="week",
            money_unit="",
            start=(2026, 11, 2),
            days_per_period=5,
            source="The conference's baseline and status reports are original to these course materials. Budgets are spread evenly over each activity's planned workdays; a week is five workdays from Mon 2 Nov 2026.",
            # id, activity, predecessors, planned duration (workdays), budget, PV by week
            tasks=[
                ("A", "Approve event brief", [], 2, 2000, {1: 2000}),
                ("B", "Contract venue", ["A"], 5, 30000, {1: 18000, 2: 12000}),
                ("C", "Draft program", ["A"], 6, 6000, {1: 3000, 2: 3000}),
                ("D", "Configure registration", ["B"], 4, 8000, {2: 6000, 3: 2000}),
                ("E", "Confirm speakers", ["C"], 8, 12000, {2: 3000, 3: 7500, 4: 1500}),
                ("F", "Recruit exhibitors", ["C"], 5, 2500, {2: 1000, 3: 1500}),
                ("G", "Publish program", ["D", "E"], 3, 3000, {4: 3000}),
                ("H", "Prepare on-site materials", ["F", "G"], 4, 4000, {4: 1000, 5: 3000}),
                ("I", "Complete rehearsal", ["H"], 2, 2500, {5: 2500}),
            ],
            # status period: {id: (percent complete, actual cost to date)}, cumulative
            status={
                1: {"A": (100, 2100), "B": (70, 20000), "C": (30, 2000)},
                2: {"A": (100, 2100), "B": (100, 28500), "C": (50, 3800), "D": (100, 7600)},
                3: {"A": (100, 2100), "B": (100, 28500), "C": (100, 6400), "D": (100, 7600), "E": (25, 3200), "F": (40, 900)},
            },
            # durations now expected at each report, in workdays (actual if finished)
            expected={1: {}, 2: {"B": 4, "C": 11}, 3: {"B": 4, "C": 11}},
            history={},
            default_period=2,
            eac_re=None,
        ),
        "The chapter's Digital Camera project (Figure 13.8, Table 13.3)": dict(
            unit="period",
            money_unit="$000",
            start=None,
            days_per_period=1,
            source="Values from Larson & Gray, Ch. 13, Figure 13.8 and Table 13.3, in $000. Totals for periods 4 to 6 are read from the chapter's Figures 13.9 and 13.12, which do not give activity detail.",
            tasks=[
                ("A", "Design specifications", [], 2, 20, {1: 10, 2: 10}),
                ("B", "Shell & power", ["A"], 2, 15, {3: 5, 4: 10}),
                ("C", "Memory/software", ["A"], 4, 100, {3: 20, 4: 30, 5: 30, 6: 20}),
                ("D", "Zoom system", ["A"], 3, 35, {3: 15, 4: 10, 5: 10}),
                ("E", "Assemble", ["B", "C", "D"], 3, 120, {7: 30, 8: 40, 9: 50}),
                ("F", "Test", ["E"], 2, 30, {10: 10, 11: 20}),
            ],
            status={
                1: {"A": (50, 10)},
                2: {"A": (100, 30)},
                3: {"A": (100, 30), "B": (100 / 3, 10), "C": (20, 30), "D": (60, 20)},
                7: {"A": (100, 30), "B": (100, 20), "C": (90, 120), "D": (100, 60)},
            },
            expected={1: {}, 2: {}, 3: {}, 7: {"C": 6}},
            history={4: (113, 150), 5: (123, 200), 6: (150, 220)},
            default_period=7,
            eac_re=575,
        ),
    }
    return (EXAMPLES,)


@app.cell(hide_code=True)
def _(EXAMPLES, mo):
    example_picker = mo.ui.radio(options=list(EXAMPLES), value=list(EXAMPLES)[0], label="**Project**")
    example_picker
    return (example_picker,)


@app.cell(hide_code=True)
def _(EXAMPLES, example_picker, mo):
    EX = EXAMPLES[example_picker.value]
    UNIT = EX["unit"]
    period_picker = mo.ui.dropdown(
        options={f"End of {UNIT} {p}": p for p in EX["status"]},
        value=f"End of {UNIT} {EX['default_period']}",
        label="**Status report**",
    )
    period_picker
    return EX, UNIT, period_picker


@app.cell(hide_code=True)
def _(EX, date, mo, timedelta):
    TASKS = {a: dict(name=nm, pred=p, n=n, budget=b, pv=pv) for a, nm, p, n, b, pv in EX["tasks"]}
    IDS = list(TASKS)
    BAC = sum(t["budget"] for t in TASKS.values())
    LAST = max(max(t["pv"]) for t in TASKS.values())
    PU = EX["money_unit"]

    def pv_task(a, period):
        return sum(v for p, v in TASKS[a]["pv"].items() if p <= period)

    def pv_total(period):
        return sum(pv_task(a, period) for a in IDS)

    def cpm(dur):
        es, ef = {}, {}
        for a in IDS:
            es[a] = max([ef[p] for p in TASKS[a]["pred"]], default=0)
            ef[a] = es[a] + dur[a]
        return es, ef

    def workday_date(n):
        if EX["start"] is None:
            return None
        day, left = date(*EX["start"]), n - 1
        while left:
            day += timedelta(days=1)
            if day.weekday() < 5:
                left -= 1
        return day.strftime("%a %-d %b")

    def money(v):
        # escaped, because marimo markdown reads a pair of bare dollar signs as mathematics
        s = f"{abs(v):,.0f}" if abs(v) >= 1000 or float(v).is_integer() else f"{abs(v):,.1f}"
        return ("−" if v < 0 else "") + "\\$" + s

    def signed(v):
        return ("+" if v > 0 else "−" if v < 0 else "") + money(abs(v)).replace("−", "")

    def md_table(rows, cols, align):
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(align) + "|"]
        lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
        return mo.md("\n".join(lines))

    return BAC, IDS, LAST, PU, TASKS, cpm, md_table, money, pv_task, pv_total, signed, workday_date


@app.cell(hide_code=True)
def _(BAC, EX, IDS, LAST, PU, TASKS, UNIT, md_table, mo, money, pv_total):
    _periods = list(range(1, LAST + 1))
    _rows = [[a, TASKS[a]["name"], money(TASKS[a]["budget"])] + [money(TASKS[a]["pv"][p]) if p in TASKS[a]["pv"] else "" for p in _periods] for a in IDS]
    _rows.append(["", "**PV this " + UNIT + "**", ""] + [money(pv_total(p) - pv_total(p - 1)) for p in _periods])
    _rows.append(["", "**Cumulative PV**", f"**{money(BAC)}**"] + [f"**{money(pv_total(p))}**" for p in _periods])
    mo.vstack(
        [
            mo.md(f"## 1 · The baseline{' (' + PU + ')' if PU else ''}"),
            mo.md(f"Each activity's budget is laid out over the {UNIT}s it was planned to run. Add down a column for that {UNIT}'s PV; add across the bottom row for the cumulative PV, the curve every report is compared with."),
            md_table(_rows, ["ID", "Activity", "Budget"] + [str(p) for p in _periods], [":-:", ":--", "--:"] + ["--:"] * len(_periods)),
            mo.md(f"*{EX['source']}*"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · The status report

    Each activity's **percent complete** and **actual cost to date** come from the people doing the work. Start from the report as given, or change it and watch every measure respond. With *Show the answers* off, work the worksheet by hand first.
    """)
    return


@app.cell(hide_code=True)
def _(EX, IDS, PU, TASKS, mo, period_picker):
    _rep = EX["status"][period_picker.value]
    pct_inputs = mo.ui.dictionary(
        {a: mo.ui.slider(0, 100, step=1, value=round(_rep.get(a, (0, 0))[0]), show_value=True, label=f"{a} · % complete") for a in IDS}
    )
    ac_inputs = mo.ui.dictionary(
        {a: mo.ui.number(start=0, stop=10 * TASKS[a]["budget"], step=1 if PU else 100, value=_rep.get(a, (0, 0))[1], label=f"actual cost{' (' + PU + ')' if PU else ''}") for a in IDS}
    )
    rule_picker = mo.ui.radio(options=["Percent complete", "50/50", "0/100"], value="Percent complete", label="**Earning rule**", inline=True)
    show_answers = mo.ui.switch(value=False, label="**Show the answers**")
    return ac_inputs, pct_inputs, rule_picker, show_answers


@app.cell(hide_code=True)
def _(IDS, TASKS, ac_inputs, mo, pct_inputs, rule_picker, show_answers):
    mo.vstack(
        [mo.hstack([rule_picker, show_answers], justify="space-between")]
        + [mo.hstack([mo.md(f"**{a}** {TASKS[a]['name']}").style({"width": "210px"}), pct_inputs[a], ac_inputs[a]], justify="start", gap=1.5) for a in IDS]
    )
    return


@app.cell(hide_code=True)
def _(BAC, EX, IDS, TASKS, ac_inputs, pct_inputs, period_picker, pv_task, rule_picker):
    PERIOD = period_picker.value
    # the slider holds whole percents; keep a report's exact value (the chapter's 33% for B is a third) until it is moved
    _given = EX["status"][PERIOD]

    def _pct(a):
        g = _given.get(a, (0, 0))[0]
        return g if round(g) == pct_inputs.value[a] and abs(g - round(g)) > 0 else pct_inputs.value[a]

    def _earned(a):
        p, b = _pct(a), TASKS[a]["budget"]
        if rule_picker.value == "Percent complete":
            return b * p / 100
        if p >= 100:
            return b
        return b / 2 if rule_picker.value == "50/50" and p > 0 else 0.0

    ROWS = [dict(id=a, pct=_pct(a), EV=_earned(a), AC=ac_inputs.value[a], PV=pv_task(a, PERIOD)) for a in IDS]
    EV = sum(r["EV"] for r in ROWS)
    AC = sum(r["AC"] for r in ROWS)
    PV = sum(r["PV"] for r in ROWS)
    CPI = EV / AC if AC else float("nan")
    SPI = EV / PV if PV else float("nan")
    ETC = (BAC - EV) / CPI if AC and EV else float("nan")
    EAC = AC + ETC
    M = dict(CV=EV - AC, SV=EV - PV, CPI=CPI, SPI=SPI, PCIB=EV / BAC, ETC=ETC, EAC=EAC, VAC=BAC - EAC,
             TCPI=(BAC - EV) / (BAC - AC) if BAC != AC else float("nan"))
    return AC, EV, M, PERIOD, PV, ROWS


@app.cell(hide_code=True)
def _(AC, EV, M, PERIOD, PU, PV, ROWS, TASKS, UNIT, md_table, mo, money, show_answers, signed):
    _q = "?"
    _show = show_answers.value
    _rows = []
    for r in ROWS:
        _p = "Finished" if r["pct"] >= 100 else ("—" if r["pct"] == 0 and r["AC"] == 0 else f"{r['pct']:.0f}%")
        _rows.append([r["id"], TASKS[r["id"]]["name"], _p, money(r["EV"]) if _show else _q, money(r["AC"]), money(r["PV"]) if _show else _q,
                      signed(r["EV"] - r["AC"]) if _show else _q, signed(r["EV"] - r["PV"]) if _show else _q])
    _rows.append(["", "**Cumulative totals**", "", f"**{money(EV)}**" if _show else _q, f"**{money(AC)}**", f"**{money(PV)}**" if _show else _q,
                  f"**{signed(EV - AC)}**" if _show else _q, f"**{signed(EV - PV)}**" if _show else _q])
    _table = md_table(_rows, ["ID", "Activity", "% complete", "EV", "AC", "PV", "CV = EV − AC", "SV = EV − PV"], [":-:", ":--", "--:", "--:", "--:", "--:", "--:", "--:"])

    def _fmt(k, v):
        if v != v:
            return "—"
        if k in ("CPI", "SPI", "TCPI"):
            return f"{v:.2f}"
        if k == "PCIB":
            return f"{v:.0%}"
        s = f"{abs(v):,.0f}" if abs(v) >= 100 or abs(round(v) - v) < 1e-9 else f"{abs(v):,.1f}"
        return ("−" if v < 0 else "+" if k in ("CV", "SV", "VAC") and v > 0 else "") + "$" + s

    _labels = dict(CV="Cost variance", SV="Schedule variance", CPI="CPI = EV ÷ AC", SPI="SPI = EV ÷ PV", PCIB="PCIB = EV ÷ BAC",
                   ETC="ETC = (BAC − EV) ÷ CPI", EAC="EAC = AC + ETC", VAC="VAC = BAC − EAC", TCPI="TCPI")
    _tiles = [mo.stat(value=_fmt(k, M[k]) if _show else "?", label=_labels[k]) for k in M]
    _read = ""
    if _show and M["CPI"] == M["CPI"]:
        _cost = "under" if M["CPI"] > 1.005 else "over" if M["CPI"] < 0.995 else "on"
        _sched = "ahead of" if M["SPI"] > 1.005 else "behind" if M["SPI"] < 0.995 else "on"
        _read = (f"Each dollar spent earned **{M['CPI']:.2f}** dollars of planned work: "
                 f"**{_cost} cost**. The work done is worth **{M['SPI']:.0%}** of the work scheduled: **{_sched} schedule**, in dollars. "
                 f"If the CPI holds, the project costs **{money(M['EAC'])}**, {'an overrun' if M['VAC'] < 0 else 'an underrun'} of **{money(abs(M['VAC']))}**; "
                 f"the remaining work must earn **{M['TCPI']:.2f}** per dollar left to finish on budget.")
    mo.vstack(
        [
            mo.md(f"### Status report, end of {UNIT} {PERIOD}{' (' + PU + ')' if PU else ''}"),
            _table,
            mo.hstack(_tiles[:4], widths="equal"),
            mo.hstack(_tiles[4:], widths="equal"),
            mo.md(_read) if _read else mo.md("*Fill in the worksheet, then switch on* Show the answers *to check it.*"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · The graphs

    Left: cumulative PV to the planned finish, with EV and AC at every report, and the forecast from today to EAC (the chapter's Figures 13.4 and 13.9). Right: the indexes over time (its Figure 13.12). Your current report replaces the one it was built from.
    """)
    return


@app.cell(hide_code=True)
def _(AC, BAC, EV, EX, IDS, LAST, M, PERIOD, TASKS, UNIT, alt, mo, pd, pv_total, show_answers):
    def _given_totals(p):
        rep = EX["status"][p]
        ev = sum(TASKS[a]["budget"] * rep[a][0] / 100 for a in rep)
        return ev, sum(v[1] for v in rep.values())

    _hist = {p: _given_totals(p) for p in EX["status"]}
    _hist.update(EX["history"])
    _hist[PERIOD] = (EV, AC)
    _hist = {p: v for p, v in sorted(_hist.items()) if p <= max(PERIOD, max(EX["status"]))}
    _pts = [p for p in _hist if p <= PERIOD]
    _curve = pd.DataFrame(
        [dict(period=p, value=pv_total(p), series="PV, baseline") for p in range(0, LAST + 1)]
        + [dict(period=0, value=0, series=s) for s in ("EV, earned", "AC, actual")]
        + [dict(period=p, value=_hist[p][0], series="EV, earned") for p in _pts]
        + [dict(period=p, value=_hist[p][1], series="AC, actual") for p in _pts]
    )
    _dom = ["PV, baseline", "EV, earned", "AC, actual"]
    _rng = ["#627571", "#0F5A4B", "#B5543A"]
    _dash = alt.Scale(domain=_dom, range=[[8, 5], [1, 0], [2, 4]])
    _base = alt.Chart(_curve).encode(
        x=alt.X("period:Q", title=f"{UNIT.capitalize()}s", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("value:Q", title="Cumulative cost"),
        color=alt.Color("series:N", scale=alt.Scale(domain=_dom, range=_rng), legend=alt.Legend(title=None, orient="top-left")),
        strokeDash=alt.StrokeDash("series:N", scale=_dash, legend=None),
    )
    _layers = [_base.mark_line(strokeWidth=2.5), _base.mark_point(filled=True, size=45)]
    _rules = pd.DataFrame([dict(period=PERIOD, label="today")])
    _layers.append(alt.Chart(_rules).mark_rule(color="#203331", strokeDash=[3, 3]).encode(x="period:Q"))
    _ref = pd.DataFrame([dict(y=BAC, label=f"BAC {BAC:,.0f}")])
    _layers.append(alt.Chart(_ref).mark_rule(color="#627571", strokeWidth=1).encode(y="y:Q"))
    if show_answers.value and M["EAC"] == M["EAC"]:
        _fc = pd.DataFrame([dict(period=PERIOD, value=AC), dict(period=LAST, value=M["EAC"])])
        _layers.append(alt.Chart(_fc).mark_line(color="#B5543A", strokeDash=[1, 4], strokeWidth=2).encode(x="period:Q", y="value:Q"))
    _left = alt.layer(*_layers).properties(width=430, height=300, title="Cost/schedule graph")

    _idx = []
    for p in _pts:
        ev, ac = _hist[p]
        pv = pv_total(p)
        _idx += [dict(period=p, index=ev / ac if ac else None, measure="CPI"), dict(period=p, index=ev / pv if pv else None, measure="SPI"),
                 dict(period=p, index=ev / BAC, measure="PCIB")]
    _idf = pd.DataFrame(_idx)
    _ib = alt.Chart(_idf).encode(
        x=alt.X("period:Q", title=f"{UNIT.capitalize()}s", axis=alt.Axis(tickMinStep=1), scale=alt.Scale(domain=[0, max(_pts) + 0.5])),
        y=alt.Y("index:Q", title="Index", scale=alt.Scale(domain=[0, 1.25])),
        color=alt.Color("measure:N", scale=alt.Scale(domain=["CPI", "SPI", "PCIB"], range=["#0F5A4B", "#627571", "#B5543A"]), legend=alt.Legend(title=None, orient="bottom-right")),
        strokeDash=alt.StrokeDash("measure:N", scale=alt.Scale(domain=["CPI", "SPI", "PCIB"], range=[[1, 0], [8, 5], [2, 4]]), legend=None),
    )
    _one = alt.Chart(pd.DataFrame([dict(y=1.0)])).mark_rule(color="#203331", strokeDash=[4, 3]).encode(y="y:Q")
    _right = alt.layer(_ib.mark_line(strokeWidth=2.5), _ib.mark_point(filled=True, size=45), _one).properties(width=300, height=300, title="Indexes")
    mo.ui.altair_chart(alt.hconcat(_left, _right).resolve_scale(color="independent", strokeDash="independent").configure_view(stroke=None))
    return


@app.cell(hide_code=True)
def _(EX, M, PERIOD, UNIT, mo, money, show_answers):
    eac_re_input = mo.ui.number(start=0, stop=10_000_000, step=1, value=EX["eac_re"] or round(M["EAC"]) if M["EAC"] == M["EAC"] else 0,
                                label="EAC re-estimated by the team (EACre)")
    _txt = (f"The CPI forecast, EACf, assumes the efficiency so far continues. The team can instead re-estimate the remaining work: EACre = AC + ETCre. "
            f"The chapter's team re-estimated 575 at period 7. PCIC = AC ÷ EAC reads percent complete in spent dollars instead of budgeted ones.")
    mo.vstack([mo.md(f"### Two forecasts at the end of {UNIT} {PERIOD}"), mo.md(_txt), eac_re_input]) if show_answers.value else mo.md("")
    return (eac_re_input,)


@app.cell(hide_code=True)
def _(AC, BAC, M, eac_re_input, mo, money, show_answers):
    _out = mo.md("")
    if show_answers.value and eac_re_input.value:
        _re = eac_re_input.value
        _out = mo.md(
            f"| | CPI forecast (EACf) | Team's re-estimate (EACre) |\n|:--|--:|--:|\n"
            f"| Estimate at completion | {money(M['EAC'])} | {money(_re)} |\n"
            f"| Variance at completion, BAC − EAC | {money(BAC - M['EAC'])} | {money(BAC - _re)} |\n"
            f"| Percent complete, AC ÷ EAC (PCIC) | {AC / M['EAC']:.0%} | {AC / _re:.0%} |\n\n"
            f"PCIB, the budgeted view, is **{M['PCIB']:.0%}**. With the CPI forecast, PCIC always equals PCIB; a re-estimate is what makes them differ."
        )
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · The schedule: what the dollars do not say

    SV is measured in dollars. A large activity on time can outweigh a small one that is late, even when the small one is on the critical path. Only the network says when the project finishes. The table recomputes it with each activity's actual or now-expected duration from the report.
    """)
    return


@app.cell(hide_code=True)
def _(EX, IDS, M, PERIOD, TASKS, UNIT, cpm, md_table, mo, show_answers, workday_date):
    _plan = {a: TASKS[a]["n"] for a in IDS}
    _now = dict(_plan, **EX["expected"].get(PERIOD, {}))
    _es0, _ef0 = cpm(_plan)
    _es1, _ef1 = cpm(_now)
    _T0, _T1 = max(_ef0.values()), max(_ef1.values())
    _du = "workday" if EX["start"] else UNIT
    _rows = [[a, TASKS[a]["name"], _plan[a], _now[a], _ef0[a], _ef1[a], f"{_ef1[a] - _ef0[a]:+d}" if _ef1[a] != _ef0[a] else ""] for a in IDS]
    _when = (f" ({workday_date(_T0)} planned, {workday_date(_T1)} forecast)" if EX["start"] else "")
    _msg = (f"Planned finish **{_du} {_T0}**, forecast **{_du} {_T1}**{_when}: **{_T1 - _T0:+d} {_du}s**, "
            f"{(_T1 - _T0) / _T0:.0%} of the plan. ")
    if show_answers.value and M["SPI"] == M["SPI"]:
        _msg += f"SPI says {1 - M['SPI']:.0%} of the scheduled work is missing, in dollars."
    mo.vstack(
        [
            md_table(_rows, ["ID", "Activity", "Planned duration", "Now expected", "Planned finish", "Forecast finish", "Moved"], [":-:", ":--", "--:", "--:", "--:", "--:", "--:"]),
            mo.md(_msg),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Try it

    - **Conference, week 2.** This is Tuesday's worksheet. Fill it in by hand, then switch on the answers. Which activity's dollars make SV look small, and which activity's delay moves the finish?
    - **Conference, week 3.** CPI is above 1 and VAC is positive. Read section 4, then decide whether this project is under budget once a day of indirect cost (\$1,000) is counted.
    - **Earning rules.** Switch between percent complete, 50/50 and 0/100 at week 3. Which rule flatters the report, and which is harsh?
    - **Digital Camera, period 7.** Check the chapter: CPI .70, SPI .80, EAC 460, TCPI 1.78. Set C to 100% at the same actual cost and see how much of the problem was C.
    """)
    return


if __name__ == "__main__":
    app.run()
