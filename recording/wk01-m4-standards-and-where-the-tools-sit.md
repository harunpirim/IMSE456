# Module 4
# Standards, tailoring, and where the tools sit

	IMSE 456/656 · Week 1 · Larson Ch. 1

Four documents dominate this field. Students routinely assume they are four versions of the same thing, competing for the same job. They are not. They are not even the same *kind* of document, and knowing which kind you are holding is most of the skill.

Then, at the end, I will tell you where the software in this course sits — because choosing a tool stack is itself a tailoring decision, and I have already made it for you.

---

# PMBOK 8, and the interesting part

	**A Guide to the Project Management Body of Knowledge**, Eighth Edition
	PMI — released late 2025, general availability January 2026
	
	**6 principles** (down from 12) · **7 performance domains** (down from 8)
	**40 processes**, reintroduced in deliberately non-prescriptive form

The seven domains: Governance, Scope, Schedule, Finance, Stakeholders, Resources, Risk. The six principles include one that is new as a standalone principle — integrate sustainability. It is not new to PMI's thinking; in the 7th edition it lived inside Stewardship. Being promoted to its own principle is a statement about what PMI thinks the next decade demands.

But the pedagogically interesting part is not the contents. It is the trajectory.

---

# 49 → 0 → 40

	**PMBOK 6** (2017) — 49 processes, 5 process groups, 10 knowledge areas
	**PMBOK 7** (2021) — processes thrown out, principle-based
	**PMBOK 8** (2025) — processes back, framed as non-prescriptive

Eight years, and the pendulum went all the way across and most of the way back.

Ask yourself what problem each swing was solving, because a standards body does not do this by accident.

Version 6 was a checklist, and a checklist gives practitioners something to *do* while giving them nothing to *think with* — you can execute forty-nine processes on a doomed project and feel compliant the whole way down.

Version 7 gave them principles, which are something to think with and nothing to do. Ask a graduate to "focus on value" on a Tuesday morning and watch what happens.

Version 8 is an attempt to hold both — processes for the hands, principles for the head, with the explicit instruction that tailoring is mandatory rather than permitted. Whether it works is genuinely open. You are watching a discipline argue with itself in public, and that is more interesting than any single edition.

---

# The four documents are four different kinds of thing

	| Document | What it claims to be | Governance stance |
	|---|---|---|
	| PMBOK 8 (PMI, 2025) | A body of knowledge + a standard; descriptive | Tailoring mandatory |
	| PRINCE2 (PeopleCert) | A **method** — prescriptive processes and roles | Strong: project board, stage boundaries, exceptions |
	| ISO 21502:2020 | Guidance — generic, vendor-neutral, non-certifiable | Light; written to be referenced in contracts |
	| Scrum Guide (Nov 2020) | A **framework** — immutable, deliberately incomplete | None beyond the team; silent on portfolio |

One test cuts through all of it: which of these could you sue somebody over?

ISO 21502 is written to be referenced in a contract, so a clause can require conformance and a court can read it. PRINCE2 is a method with named roles and mandatory stage boundaries, so an organization can mandate it and audit against it. PMBOK is descriptive and tells you tailoring is mandatory, which makes non-conformance almost undefinable. And the Scrum Guide announces that it is purposefully incomplete, which is a rather elegant way of saying: whatever went wrong, that was not us.

That is not cynicism. It tells you where each document expects the accountability to sit — and accountability is what you will actually be managing.

---

# The Scrum Guide has not changed since 2020

	**13 pages.** Last revised **November 2020**.
	Added the Product Goal; gave each artifact one commitment:
	Product Backlog → Product Goal · Sprint Backlog → Sprint Goal · Increment → Definition of Done

Students assume standards churn, because the ones with certification revenue attached do.

Here is the counterexample. Thirteen pages, free, unrevised for six years, and it did not become irrelevant. Hold on to that the next time someone tells you a framework was revised because knowledge advanced. Sometimes it was. Sometimes it was revised because there is an exam attached to it. The Scrum Guide is the case that makes you distinguish the two claims instead of assuming one.

---

# Tailoring: five questions, every time

	1. How much will requirements change before delivery? *High → adaptive*
	2. How expensive is a late change? *Very → predictive front-loading*
	3. Can we deliver increments a stakeholder would actually accept? *No → predictive*
	4. Is there a gate requiring a frozen baseline? *Yes → predictive at least at the gate*
	5. Is the team co-located and empowered enough to self-manage? *No → the ceremonies are theatre*

You will apply these five questions every week for the rest of the semester, and in your final project you will have to defend your answers against the literature rather than against your preferences.

Question five is the one people skip and the one that decides it. Agile ceremonies performed by a team that cannot actually make decisions are a status meeting with better vocabulary, and everyone in the room knows it by the third sprint.

---

# Where the tools in this course sit

	**Record** — Taiga · ProjectLibre · Smartsheet
	**Analysis** — Python · Power BI
	**Decision** — the dashboard somebody acts on

Choosing this stack was a tailoring decision, and I want it visible rather than hidden.

The record layer is where a commitment is written down and can be argued with. The analysis layer turns records into a claim. The decision layer is the one page an executive looks at for eleven seconds.

Every one of these layers can be wrong, but they fail differently. A wrong record is a lie about what happened. A wrong analysis is a lie about what it means. A wrong dashboard is usually neither — it is an accurate rendering of a broken record, which is why it is the most dangerous of the three. Nobody distrusts a chart.

In Week 11 I have broken a number on purpose, and the dashboard will look fine.

---

# And the AI layer runs through all three

	You will **generate** artifacts with a model — then write the code that **checks** them.
	Level 4 in the studios: generate freely, verify everything, disclose.
	**The check is graded, not the output.**

This is the part of the course that does not exist in the textbook, and it is the reason the course is worth taking in 2026 rather than 2016.

A model will produce you a work breakdown structure in nine seconds. It will be plausible, well-formatted, and it will quietly omit a stakeholder, because it does not know who is in your room. Your job is not to produce the artifact. It is to know which questions the artifact cannot answer, and to build the check that catches what it got wrong.

That is a project management skill, not a computing skill. It is the same skill as reading a contractor's schedule and knowing which activity is missing.

---

# What to hold on to

	1. Standard, method, guidance, framework — **four different kinds of document.**
	2. Ask which one you could **sue** somebody over. That tells you where accountability sits.
	3. **Tailoring is the skill.** Adopting a framework wholesale is the failure mode.
	4. Record → Analysis → Decision. The dashboard is the easiest layer to trust and the easiest to break.

That is Week 1. Bring a laptop on Thursday.
