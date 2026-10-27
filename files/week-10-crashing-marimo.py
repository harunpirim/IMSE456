# /// script
# requires-python = ">=3.10"
# dependencies = ["marimo", "altair", "pandas"]
# ///
"""Week 10 · Crashing, interactively: the chapter's example and the conference.

IMSE 456/656 · Larson & Gray, Chapter 9. Open in the browser, nothing to install:
https://marimo.app/github.com/harunpirim/IMSE456/blob/main/files/week-10-crashing-marimo.py
"""

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Week 10 · Crashing")


@app.cell(hide_code=True)
def _():
    import itertools
    from datetime import date, timedelta

    import altair as alt
    import marimo as mo
    import pandas as pd
    return alt, date, itertools, mo, pd, timedelta


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Week 10 · Crashing, interactively

    IMSE 456/656 · Program and Project Management · Larson & Gray, Chapter 9

    This notebook runs the two crashing examples from the Week 10 notes. Pick one below and work down the page:

    1. **Crash it yourself.** Shorten activities with the sliders and watch the critical paths, the finish and the three costs move.
    2. **The chapter's procedure.** Step through the least-cost procedure one unit of time at a time, with every option it weighed.
    3. **The cost-duration graph.** Direct, indirect and total cost against duration, with your own plan on it.
    4. **The exact check.** Every possible combination of crashes, tried, to confirm the procedure found the cheapest plan at every duration.

    Everything recalculates as you move a control; there is nothing to run.
    """)
    return


@app.cell(hide_code=True)
def _():
    # id, activity, predecessors, normal time, normal cost, crash time, crash cost
    EXAMPLES = {
        "The chapter's example (Figures 9.3 to 9.5)": dict(
            unit="unit",
            indirect_at_normal=400,
            indirect_rate=50,
            rate_max=150,
            rate_step=5,
            start=None,
            source="Values from Larson & Gray, Ch. 9, Figures 9.3 to 9.5. Time is in units; indirect cost is $400 at 25 units and falls $50 a unit.",
            rows=[
                ("A", "Activity A", [], 3, 50, 2, 70),
                ("B", "Activity B", ["A"], 6, 80, 4, 160),
                ("C", "Activity C", ["A"], 10, 60, 9, 90),
                ("D", "Activity D", ["A"], 11, 50, 7, 150),
                ("E", "Activity E", ["B"], 8, 100, 6, 160),
                ("F", "Activity F", ["C", "D"], 5, 40, 4, 70),
                ("G", "Activity G", ["E", "F"], 6, 70, 6, 70),
            ],
        ),
        "The conference": dict(
            unit="workday",
            indirect_at_normal=25000,
            indirect_rate=1000,
            rate_max=2000,
            rate_step=50,
            start=(2026, 11, 2),
            source="Crash estimates original to these course materials. Workdays, Monday to Friday from Mon 2 Nov 2026; indirect cost is $1,000 a workday.",
            rows=[
                ("A", "Approve event brief", [], 2, 2000, 1, 3200),
                ("B", "Contract venue", ["A"], 5, 30000, 3, 31400),
                ("C", "Draft program", ["A"], 6, 6000, 4, 6800),
                ("D", "Configure registration", ["B"], 4, 8000, 3, 8900),
                ("E", "Confirm speakers", ["C"], 8, 12000, 5, 13800),
                ("F", "Recruit exhibitors", ["C"], 5, 2500, 3, 3100),
                ("G", "Publish program", ["D", "E"], 3, 3000, 2, 4500),
                ("H", "Prepare on-site materials", ["F", "G"], 4, 4000, 2, 5600),
                ("I", "Complete rehearsal", ["H"], 2, 2500, 2, 2500),
            ],
        ),
    }
    return (EXAMPLES,)


@app.cell(hide_code=True)
def _(EXAMPLES, mo):
    example_picker = mo.ui.radio(options=list(EXAMPLES), value=list(EXAMPLES)[0], label="**Example**")
    example_picker
    return (example_picker,)


@app.cell(hide_code=True)
def _(EXAMPLES, example_picker):
    EX = EXAMPLES[example_picker.value]
    ACT = {a: dict(name=nm, pred=p, n=n, nc=nc, c=c, cc=cc) for a, nm, p, n, nc, c, cc in EX["rows"]}
    IDS = list(ACT)
    UNIT = EX["unit"]
    return ACT, EX, IDS, UNIT


@app.cell(hide_code=True)
def _(ACT, EX, IDS, date, mo, timedelta):
    def slope(a):
        x = ACT[a]
        return (x["cc"] - x["nc"]) / (x["n"] - x["c"]) if x["n"] > x["c"] else None

    def can_save(a):
        return ACT[a]["n"] - ACT[a]["c"]

    def all_paths():
        succ = {a: [s for s in IDS if a in ACT[s]["pred"]] for a in IDS}
        out = []

        def walk(a, so_far):
            if not succ[a]:
                out.append(so_far + [a])
                return
            for s in succ[a]:
                walk(s, so_far + [a])

        for a in IDS:
            if not ACT[a]["pred"]:
                walk(a, [])
        return out

    PATHS = all_paths()
    NORMAL_T = max(sum(ACT[a]["n"] for a in p) for p in PATHS)
    NORMAL_DIRECT = sum(ACT[a]["nc"] for a in IDS)

    def durations(cut):
        return {a: ACT[a]["n"] - cut.get(a, 0) for a in IDS}

    def path_lengths(cut):
        d = durations(cut)
        return [sum(d[a] for a in p) for p in PATHS]

    def direct_cost(cut):
        return NORMAL_DIRECT + sum((slope(a) or 0) * cut.get(a, 0) for a in IDS)

    def indirect_cost(T, rate):
        return EX["indirect_at_normal"] - rate * (NORMAL_T - T)

    def name(p):
        return "–".join(p)

    def finish(T):
        """Calendar finish of a T-workday project, Monday to Friday, no holidays."""
        if EX["start"] is None:
            return None
        day, left = date(*EX["start"]), T - 1
        while left:
            day += timedelta(days=1)
            if day.weekday() < 5:
                left -= 1
        return day.strftime("%a %-d %b")

    def money(v):
        # escaped, because marimo markdown reads a pair of bare dollar signs as mathematics
        return f"\\${v:,.0f}"

    def md_table(df):
        """A data frame as a plain markdown table: numbers and dollars right-aligned, text left."""
        def right(v):
            t = str(v).replace("\\", "").replace("$", "").replace(",", "")
            return t.replace(".", "", 1).isdigit()
        cols = list(df.columns)
        align = ["--:" if right(df[c].iloc[0]) or right(df[c].iloc[-1]) else ":--" for c in cols]
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(align) + "|"]
        lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
        return mo.md("\n".join(lines))

    return (
        NORMAL_DIRECT,
        NORMAL_T,
        PATHS,
        can_save,
        direct_cost,
        finish,
        indirect_cost,
        md_table,
        money,
        name,
        path_lengths,
        slope,
    )


@app.cell(hide_code=True)
def _(ACT, EX, IDS, NORMAL_DIRECT, NORMAL_T, PATHS, UNIT, can_save, md_table, mo, money, name, pd, slope):
    _table = pd.DataFrame(
        [
            {
                "ID": a,
                "Activity": ACT[a]["name"],
                "Predecessors": ", ".join(ACT[a]["pred"]) or "—",
                "Normal time": ACT[a]["n"],
                "Normal cost": money(ACT[a]["nc"]),
                "Crash time": ACT[a]["c"],
                "Crash cost": money(ACT[a]["cc"]),
                f"Cost per {UNIT} saved": money(slope(a)) if slope(a) is not None else "—",
                "Can save": can_save(a),
            }
            for a in IDS
        ]
    )
    _paths = " · ".join(f"**{name(p)}** {sum(ACT[a]['n'] for a in p)}" for p in PATHS)
    mo.vstack(
        [
            mo.md("## The data"),
            md_table(_table),
            mo.md(
                f"Normal duration **{NORMAL_T} {UNIT}s**, normal direct cost **{money(NORMAL_DIRECT)}**. "
                f"Paths and their normal lengths: {_paths}."
            ),
            mo.md(f"*{EX['source']}*"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(EX, UNIT, mo):
    rate_slider = mo.ui.slider(
        start=0,
        stop=EX["rate_max"],
        step=EX["rate_step"],
        value=EX["indirect_rate"],
        label=f"**Indirect cost per {UNIT}** (dollars saved by finishing one {UNIT} sooner)",
        show_value=True,
        full_width=True,
    )
    rate_slider
    return (rate_slider,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · Crash it yourself

    Each slider shortens one activity. An activity that cannot be shortened has no slider. Shorten one unit at a time and read three things: did the finish move, which paths are now critical, and did the total fall?
    """)
    return


@app.cell(hide_code=True)
def _(ACT, IDS, UNIT, can_save, mo, money, slope):
    cut_sliders = mo.ui.dictionary(
        {
            a: mo.ui.slider(
                start=0,
                stop=can_save(a),
                step=1,
                value=0,
                show_value=True,
                label=f"{a} · {ACT[a]['name']} · {money(slope(a))}/{UNIT}",
            )
            for a in IDS
            if can_save(a) > 0
        }
    )
    return (cut_sliders,)


@app.cell(hide_code=True)
def _(
    ACT,
    IDS,
    NORMAL_T,
    PATHS,
    UNIT,
    alt,
    cut_sliders,
    direct_cost,
    finish,
    indirect_cost,
    mo,
    money,
    name,
    path_lengths,
    pd,
    rate_slider,
):
    my_cut = {a: v for a, v in cut_sliders.value.items() if v}
    my_T = max(path_lengths(my_cut))
    my_direct = direct_cost(my_cut)
    my_total = my_direct + indirect_cost(my_T, rate_slider.value)

    _lens = path_lengths(my_cut)
    _crit = [p for p, L in zip(PATHS, _lens) if L == my_T]
    # a crashed activity bought nothing if every path through it has slack: undoing one unit would not move the finish
    _wasted = [
        a for a in my_cut if all(L < my_T for p, L in zip(PATHS, _lens) if a in p)
    ]

    _stats = mo.hstack(
        [
            mo.stat(f"{my_T} {UNIT}s", label="Duration", caption=finish(my_T) or f"normal {NORMAL_T}"),
            mo.stat(f"${my_direct:,.0f}", label="Direct"),
            mo.stat(f"${indirect_cost(my_T, rate_slider.value):,.0f}", label="Indirect"),
            mo.stat(f"${my_total:,.0f}", label="Total", bordered=True),
        ],
        widths="equal",
    )
    _bars = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Path": [name(p) for p in PATHS],
                    "Length": _lens,
                    "Status": ["Critical" if L == my_T else f"{my_T - L} {UNIT}s of slack" for L in _lens],
                }
            )
        )
        .mark_bar()
        .encode(
            y=alt.Y("Path:N", sort=None, title=None),
            x=alt.X("Length:Q", title=f"Path length ({UNIT}s)", scale=alt.Scale(domain=[0, NORMAL_T])),
            color=alt.condition(alt.datum.Status == "Critical", alt.value("#0F5A4B"), alt.value("#B8C9C4")),
            tooltip=["Path", "Length", "Status"],
        )
        .properties(height=36 * len(PATHS), width="container")
    )
    _notes = []
    if _wasted:
        _notes.append(
            mo.callout(
                mo.md(
                    f"**Money for nothing:** {', '.join(_wasted)} {'is' if len(_wasted) == 1 else 'are'} crashed but not on any critical path. "
                    f"Undo {'it' if len(_wasted) == 1 else 'them'} and the finish does not move."
                ),
                kind="warn",
            )
        )
    _notes.append(
        mo.md(
            "Critical now: " + ", ".join(f"**{name(p)}**" for p in _crit)
            + (". Every one of them must be cut to gain the next unit." if len(_crit) > 1 else ".")
        )
    )
    mo.vstack([mo.vstack([cut_sliders[a] for a in cut_sliders]), _stats, _bars, *_notes])
    return my_T, my_total


@app.cell(hide_code=True)
def _(IDS, PATHS, can_save, direct_cost, itertools, path_lengths, slope):
    def procedure():
        """The chapter's least-cost procedure: cut every critical path by one unit at the lowest cost, until no cut is possible."""
        cut = {a: 0 for a in IDS}
        steps = []
        while True:
            lens = path_lengths(cut)
            T = max(lens)
            crit = [p for p, L in zip(PATHS, lens) if L == T]
            free = [a for a in IDS if cut[a] < can_save(a)]
            options = []
            for k in range(1, len(free) + 1):
                for combo in itertools.combinations(free, k):
                    covers = all(any(a in p for a in combo) for p in crit)
                    # keep only combinations with no activity that is redundant to the cut
                    minimal = covers and all(
                        not all(any(b in p for b in combo if b != a) for p in crit) for a in combo
                    )
                    if minimal:
                        options.append((sum(slope(a) for a in combo), combo))
            options.sort(key=lambda o: (o[0], len(o[1]), o[1]))
            steps.append(dict(T=T, cut=dict(cut), direct=direct_cost(cut), crit=crit, options=options))
            if not options:
                return steps
            for a in options[0][1]:
                cut[a] += 1

    STEPS = procedure()
    return (STEPS,)


@app.cell(hide_code=True)
def _(STEPS, UNIT, mo):
    step_slider = mo.ui.slider(
        start=0,
        stop=len(STEPS) - 1,
        step=1,
        value=0,
        label=f"**Units of time bought** (0 is the normal plan)",
        show_value=True,
        full_width=True,
    )
    mo.vstack(
        [
            mo.md(rf"""
    ## 2 · The chapter's procedure

    1. Find the critical path or paths.
    2. Among critical activities that can still be shortened, choose the cheapest way to cut **every** critical path by one {UNIT}.
    3. Shorten, add its cost to the direct cost, and recompute the paths.
    4. Repeat until no critical path can be shortened.

    Move the slider to step through it.
    """),
            step_slider,
        ]
    )
    return (step_slider,)


@app.cell(hide_code=True)
def _(STEPS, UNIT, indirect_cost, mo, money, name, rate_slider, step_slider):
    _s = STEPS[step_slider.value]
    _rate = rate_slider.value
    _total = _s["direct"] + indirect_cost(_s["T"], _rate)
    _crashed = ", ".join(f"{a} −{v}" for a, v in _s["cut"].items() if v) or "nothing yet"
    _lines = [
        f"**At {_s['T']} {UNIT}s.** Crashed so far: {_crashed}. "
        f"Direct {money(_s['direct'])}, indirect {money(indirect_cost(_s['T'], _rate))}, total **{money(_total)}**.",
        "",
        "Critical: " + ", ".join(f"**{name(p)}**" for p in _s["crit"]) + ".",
        "",
    ]
    if _s["options"]:
        _best = _s["options"][0][0]
        _lines += [f"Ways to cut every critical path by one {UNIT}, cheapest first:", "", f"| Cut | Cost of the {UNIT} | |", "|:--|--:|:--|"]
        _lines += [
            f"| {' + '.join(combo)} | {money(cost)} | {'**chosen**' if i == 0 else ''} |"
            for i, (cost, combo) in enumerate(_s["options"][:6])
        ]
        _lines += [
            "",
            f"The next {UNIT} costs **{money(_best)}** and saves **{money(_rate)}** of indirect cost: "
            + ("**buy it.**" if _best < _rate else "**stop here.** It costs more than it saves." if _best > _rate else "it breaks even."),
        ]
    else:
        _lines.append(f"No critical path can be shortened any further: **{_s['T']} {UNIT}s is the shortest possible duration.**")
    mo.md("\n".join(_lines))
    return


@app.cell(hide_code=True)
def _(STEPS, UNIT, finish, indirect_cost, md_table, mo, money, pd, rate_slider):
    _rate = rate_slider.value
    _rows = []
    for _i, _s in enumerate(STEPS):
        _prev = STEPS[_i - 1] if _i else None
        _chosen = _prev["options"][0] if _prev else None
        _rows.append(
            {
                "Duration": _s["T"],
                "Shorten": " + ".join(_chosen[1]) if _chosen else "—",
                f"Cost of the {UNIT}": money(_chosen[0]) if _chosen else "",
                "Direct": _s["direct"],
                "Indirect": indirect_cost(_s["T"], _rate),
                "Total": _s["direct"] + indirect_cost(_s["T"], _rate),
                "Finish": finish(_s["T"]) or "",
            }
        )
    procedure_table = pd.DataFrame(_rows)
    _best = procedure_table.loc[procedure_table["Total"].idxmin()]
    _show = procedure_table.copy()
    for _c in ("Direct", "Indirect", "Total"):
        _show[_c] = _show[_c].map(money)
    if not _show["Finish"].any():
        _show = _show.drop(columns="Finish")
    mo.vstack(
        [
            mo.md(f"The whole run at **{money(_rate)}** of indirect cost per {UNIT}:"),
            md_table(_show),
            mo.callout(
                mo.md(
                    f"**Optimum: {int(_best['Duration'])} {UNIT}s"
                    + (f", {_best['Finish']}" if _best["Finish"] else "")
                    + f", total {money(_best['Total'])}.** Move the indirect-cost slider above and watch it shift."
                ),
                kind="success",
            ),
        ]
    )
    return (procedure_table,)


@app.cell(hide_code=True)
def _(UNIT, alt, mo, my_T, my_total, pd, procedure_table):
    _best = procedure_table.loc[procedure_table["Total"].idxmin()]
    _x = alt.X(
        "Duration:Q",
        title=f"Project duration ({UNIT}s)",
        scale=alt.Scale(zero=False, nice=False, padding=12),
        axis=alt.Axis(tickMinStep=1, format="d"),
    )
    _money = alt.Axis(format="$,.0f")
    _total = (
        alt.Chart(procedure_table)
        .mark_line(point=True, color="#0F5A4B")
        .encode(x=_x, y=alt.Y("Total:Q", title="Total cost", scale=alt.Scale(zero=False), axis=_money),
                tooltip=["Duration", alt.Tooltip("Total:Q", format="$,.0f")])
    )
    _opt = (
        alt.Chart(pd.DataFrame([{"Duration": _best["Duration"], "Total": _best["Total"], "Label": "optimum"}]))
        .mark_point(size=260, shape="diamond", filled=True, color="#0F5A4B")
        .encode(x="Duration:Q", y="Total:Q", tooltip=["Label", "Duration", alt.Tooltip("Total:Q", format="$,.0f")])
    )
    _mine = (
        alt.Chart(pd.DataFrame([{"Duration": my_T, "Total": my_total, "Label": "your plan"}]))
        .mark_point(size=170, shape="circle", filled=True, color="#B3412F")
        .encode(x="Duration:Q", y="Total:Q", tooltip=["Label", "Duration", alt.Tooltip("Total:Q", format="$,.0f")])
    )
    _parts = (
        alt.Chart(procedure_table.melt(id_vars="Duration", value_vars=["Direct", "Indirect"], var_name="Cost", value_name="Dollars"))
        .mark_line(point=True)
        .encode(
            x=_x,
            y=alt.Y("Dollars:Q", title="Direct and indirect", scale=alt.Scale(zero=False), axis=_money),
            color=alt.Color("Cost:N", scale=alt.Scale(domain=["Direct", "Indirect"], range=["#7A8F89", "#C08A3E"]),
                            legend=alt.Legend(orient="right", title=None)),
            tooltip=["Duration", "Cost", alt.Tooltip("Dollars:Q", format="$,.0f")],
        )
    )
    _chart = alt.vconcat(
        (_total + _opt + _mine).properties(height=220, width=620, title="Total cost"),
        _parts.properties(height=200, width=620, title="Its two parts"),
    )
    mo.vstack(
        [
            mo.md(
                f"""
    ## 3 · The cost-duration graph

    Read the lower chart first: as the project is compressed, direct cost rises and indirect cost falls. The upper chart is their sum. The diamond is the optimum. The red dot is **your plan** from section 1: if it sits above the line, the same duration could have been bought for less.
    """
            ),
            _chart,
        ]
    )
    return


@app.cell(hide_code=True)
def _(
    IDS,
    NORMAL_DIRECT,
    STEPS,
    UNIT,
    can_save,
    direct_cost,
    itertools,
    md_table,
    mo,
    money,
    path_lengths,
    pd,
):
    # try every combination of whole-unit crashes and keep the cheapest direct cost at each duration
    _cheapest = {}
    for _combo in itertools.product(*[range(can_save(a) + 1) for a in IDS]):
        _cut = dict(zip(IDS, _combo))
        _T = max(path_lengths(_cut))
        _d = direct_cost(_cut)
        if _T not in _cheapest or _d < _cheapest[_T]:
            _cheapest[_T] = _d
    _n = 1
    for _a in IDS:
        _n *= can_save(_a) + 1
    _rows = [
        {
            "Duration": s["T"],
            "Procedure's direct cost": money(s["direct"]),
            "Cheapest possible": money(_cheapest[s["T"]]),
            "Agree": "yes" if abs(s["direct"] - _cheapest[s["T"]]) < 1e-6 else "NO",
        }
        for s in STEPS
    ]
    _agree = all(r["Agree"] == "yes" for r in _rows)
    _shortest = min(_cheapest)
    mo.vstack(
        [
            mo.md(
                f"""
    ## 4 · The exact check

    The procedure is a rule of thumb. To check it, this cell tries **every** combination of whole-{UNIT} crashes, {_n:,} of them, and keeps the cheapest direct cost at each duration.
    """
            ),
            md_table(pd.DataFrame(_rows)),
            mo.callout(
                mo.md(
                    (
                        f"**The procedure found the cheapest plan at every duration.** The shortest duration any combination reaches is {_shortest} {UNIT}s."
                        if _agree
                        else "**The procedure missed a cheaper plan at the duration marked NO.** On some networks it must un-crash an earlier choice to get there; the chapter's procedure never does."
                    )
                ),
                kind="success" if _agree else "danger",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(UNIT, mo):
    mo.md(rf"""
    ## Try it

    - **Crash everything.** In section 1, set every slider to its maximum. What does the project cost, and which crashes bought no time?
    - **Move the price of a {UNIT}.** For the conference, set the indirect cost to \$700, then \$1,300. Which activity's cost per day explains each new optimum?
    - **Beat the procedure.** In section 1, reach the optimum duration with a lower total than section 2. (You cannot; section 4 says why.)
    """)
    return


if __name__ == "__main__":
    app.run()
