"""Streamlit の見た目まわり。ロジックは持たない。"""
from __future__ import annotations

import html

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stChatMessage, .stDataFrame { font-family: "Noto Sans JP", "Hiragino Sans", "Yu Gothic", sans-serif; }
#MainMenu, footer, header [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton { display: none !important; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1180px; }
section[data-testid="stSidebar"] { background: #1F2A37; }
section[data-testid="stSidebar"] * { color: #E6EBF0; }
section[data-testid="stSidebar"] .stRadio label p { font-size: 14px; }
section[data-testid="stSidebar"] hr { border-color: #34424F; }
section[data-testid="stSidebar"] .stButton button { background: #2B3948; border: 1px solid #3B4A5A; color: #E6EBF0; }
section[data-testid="stSidebar"] .stButton button:hover { border-color: #AAB4BE; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #FFFFFF; border-color: #FFFFFF; }
section[data-testid="stSidebar"] [data-baseweb="select"] *, section[data-testid="stSidebar"] [data-baseweb="select"] input { color: #1F2A37 !important; -webkit-text-fill-color: #1F2A37 !important; opacity: 1 !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #1F2A37; }
h1, h2, h3 { color: #1F2A37; letter-spacing: .01em; }
h2 { font-size: 1.45rem !important; margin-top: .2rem !important; }
.mk-eyebrow { font-size: 12px; color: #5B6570; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 2px; }
.mk-title { font-size: 22px; font-weight: 700; color: #1F2A37; margin: 0 0 2px; }
.mk-sub { font-size: 13px; color: #5B6570; margin: 0 0 14px; }
.mk-card { background: #FFFFFF; border: 1px solid #E1E6EB; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; box-shadow: 0 1px 2px rgba(31,42,55,.04); }
.mk-card.soft { background: #F6F8FA; border-color: #E9EDF1; }
.mk-card h4 { margin: 0 0 8px; font-size: 14px; color: #5B6570; font-weight: 500; letter-spacing: .04em; }
.mk-row { display: flex; gap: 12px; align-items: flex-start; padding: 9px 0; border-top: 1px solid #EEF1F4; }
.mk-row:first-of-type { border-top: 0; }
.mk-dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 7px; flex: 0 0 10px; }
.mk-row .t { font-size: 15px; font-weight: 600; color: #1F2A37; }
.mk-row .d { font-size: 13px; color: #5B6570; margin-top: 2px; line-height: 1.55; }
.mk-row .due { font-variant-numeric: tabular-nums; font-weight: 700; color: #1F2A37; margin-left: 8px; }
.mk-badge { display: inline-block; font-size: 12px; font-weight: 600; padding: 2px 9px; border-radius: 999px; line-height: 1.6; white-space: nowrap; }
.b-red { background: #FBE9E5; color: #9C3A27; } .b-yellow { background: #FFF3D6; color: #8A5A00; } .b-green { background: #E3F3E8; color: #1E6B3A; }
.b-gray { background: #EDF0F3; color: #4A5560; } .b-blue { background: #E4EEF9; color: #1F4E8A; } .b-wait { background: #F1F4F7; color: #5B6570; }
.mk-finding { display: flex; gap: 12px; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border: 1px solid transparent; }
.mk-finding.f-red { background: #FDF3F1; border-color: #F3D3CC; } .mk-finding.f-yellow { background: #FFF9EC; border-color: #F5E4BE; } .mk-finding.f-green { background: #F1F9F3; border-color: #CFE8D7; }
.mk-finding .m { font-size: 14px; color: #1F2A37; line-height: 1.55; }
.mk-finding .a { font-size: 13px; color: #5B6570; margin-top: 2px; }
.mk-finding .id { font-size: 11px; color: #8A94A0; font-variant-numeric: tabular-nums; }
.mk-stat { background: #F6F8FA; border-radius: 10px; padding: 12px 16px; }
.mk-stat .l { font-size: 12px; color: #5B6570; } .mk-stat .v { font-size: 26px; font-weight: 700; color: #1F2A37; font-variant-numeric: tabular-nums; line-height: 1.2; margin-top: 2px; }
.mk-stat .v.red { color: #B5442D; } .mk-stat .h { font-size: 12px; color: #5B6570; margin-top: 4px; }
.mk-step { display: grid; grid-template-columns: 120px 22px 1fr; gap: 0 12px; }
.mk-step .date { font-variant-numeric: tabular-nums; font-weight: 600; color: #1F2A37; font-size: 14px; padding-top: 2px; text-align: right; }
.mk-step .date.none { color: #AAB4BE; font-weight: 500; }
.mk-step .line { position: relative; }
.mk-step .line:before { content: ""; position: absolute; left: 9px; top: 0; bottom: 0; width: 2px; background: #E1E6EB; }
.mk-step .line .c { position: relative; width: 12px; height: 12px; border-radius: 50%; background: #FFFFFF; border: 2px solid #1F2A37; margin: 5px 0 0 4px; }
.mk-step .line .c.fix { background: #1F2A37; } .mk-step .line .c.none { border-color: #C9D1D9; }
.mk-step .body { padding: 0 0 18px; }
.mk-step .body .t { font-size: 15px; font-weight: 600; color: #1F2A37; }
.mk-step .body .d { font-size: 13px; color: #5B6570; line-height: 1.55; margin-top: 2px; }
.mk-step .body .docs { font-size: 12px; color: #1F4E8A; margin-top: 3px; }
.mk-rule { padding: 8px 0; border-top: 1px solid #EEF1F4; font-size: 13.5px; line-height: 1.55; }
.mk-rule .q { color: #5B6570; font-size: 12.5px; }
.mk-field { display: grid; grid-template-columns: minmax(140px, 28%) 1fr auto; gap: 10px; padding: 7px 0; border-top: 1px solid #EEF1F4; font-size: 13.5px; }
.mk-field .k { color: #5B6570; } .mk-field .v { color: #1F2A37; white-space: pre-wrap; }
.stChatMessage { border-radius: 10px; }
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
div[data-testid="stExpander"] details { border-radius: 10px; border-color: #E1E6EB; }
.stButton button[kind="primary"] { background: #1F2A37; border-color: #1F2A37; }
.stButton button[kind="primary"]:hover { background: #2B3948; border-color: #2B3948; }
.stDownloadButton button { border-color: #1F2A37; color: #1F2A37; }
</style>
"""

STATUS_CLASS = {"期限超過": "b-red", "報告待ち": "b-yellow", "更新待ち": "b-yellow", "申請中": "b-gray", "交付済": "b-blue", "報告済": "b-green", "登録済": "b-green"}
LEVEL_DOT = {"now": "#B5442D", "soon": "#D99A00", "wait": "#8A94A0", "late": "#B5442D"}
FINDING_CLASS = {"不足": "f-red", "注意": "f-yellow", "OK": "f-green"}
FINDING_BADGE = {"不足": "b-red", "注意": "b-yellow", "OK": "b-green"}


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def e(s) -> str:
    return html.escape("" if s is None else str(s))


def badge(text: str, cls: str | None = None) -> str:
    return f'<span class="mk-badge {cls or STATUS_CLASS.get(text, "b-gray")}">{e(text)}</span>'


def header(profile, mode: str):
    st.markdown(
        f'<div class="mk-eyebrow">{e(profile.name)}　{e(profile.program_name)}</div>'
        f'<div class="mk-title">{"市民面（活動者）" if mode == "citizen" else "自治体面（" + e(profile.office) + "）"}</div>'
        f'<div class="mk-sub">{"地域の同意が済んだ後から完了報告まで。捕獲の手順・自治会への説得・里親探し・子猫の育て方は扱いません。" if mode == "citizen" else "市民面で提出された申請・報告がそのまま載ります。状態は要綱から抽出した期限ルールと報告履歴から計算します。"}</div>',
        unsafe_allow_html=True,
    )


def next_actions_card(acts: list[dict], rec: dict | None, status: str | None, has_spec: bool):
    head = "次にやること"
    meta = f'<span style="font-size:12px;color:#5B6570;margin-left:10px">台帳ID {e(rec["id"])}　{badge(status)}</span>' if rec else ""
    rows = []
    for x in acts:
        due = f'<span class="due">期限 {e(x["due"])}</span>' if x["due"] else ""
        docs = f'<div class="d">提出物：{e("、".join(x["docs"]))}</div>' if x["docs"] else ""
        rows.append(
            f'<div class="mk-row"><div class="mk-dot" style="background:{LEVEL_DOT[x["level"]]}"></div>'
            f'<div><div class="t">{e(x["title"])}{due}</div><div class="d">{e(x["note"])}</div>{docs}</div></div>'
        )
    tail = '<div class="d" style="font-size:12px;color:#8A94A0;margin-top:6px">要綱から工程を抽出すると、様式名と期限が入ります（5. 日程表）。</div>' if not has_spec else ""
    st.markdown(f'<div class="mk-card"><h4>{head}{meta}</h4>{"".join(rows)}{tail}</div>', unsafe_allow_html=True)


def findings(items: list[dict], ready: bool):
    n_lack = sum(1 for x in items if x["level"] == "不足")
    n_warn = sum(1 for x in items if x["level"] == "注意")
    if ready:
        st.markdown(f'<div class="mk-finding f-green"><div><div class="m"><b>不足なし。</b>申請できます。注意 {n_warn} 件を確認してください。</div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="mk-finding f-red"><div><div class="m"><b>不足 {n_lack} 件。</b>申請前に解消してください。注意 {n_warn} 件。</div></div></div>', unsafe_allow_html=True)
    order = {"不足": 0, "注意": 1, "OK": 2}
    for x in sorted(items, key=lambda x: order.get(x["level"], 9)):
        act = f'<div class="a">→ {e(x["action"])}</div>' if x.get("action") else ""
        st.markdown(
            f'<div class="mk-finding {FINDING_CLASS[x["level"]]}"><div>{badge(x["level"], FINDING_BADGE[x["level"]])}<div class="id">{e(x["rule_id"])}</div></div>'
            f'<div><div class="m">{e(x["message"])}</div>{act}</div></div>',
            unsafe_allow_html=True,
        )


def rules_list(rules: list[dict]):
    rows = "".join(
        f'<div class="mk-rule"><b>{e(r["id"])}</b>　{badge(r["category"], "b-gray")}　{e(r["requirement"])}'
        f'<div class="q">適用：{e(r["applies_when"])}／出典：{e(r["source_file"])}「{e(r["source_quote"])}」</div></div>'
        for r in rules
    )
    st.markdown(f'<div class="mk-card soft">{rows}</div>', unsafe_allow_html=True)


def stat(label: str, value: str, hint: str = "", red: bool = False):
    st.markdown(f'<div class="mk-stat"><div class="l">{e(label)}</div><div class="v{" red" if red else ""}">{e(value)}</div><div class="h">{e(hint)}</div></div>', unsafe_allow_html=True)


def timeline(rows):
    parts = []
    for r in rows:
        date = r.date.strftime("%Y-%m-%d") if r.date else "未定"
        fixed = r.key in ("annual_report", "renewal")
        docs = f'<div class="docs">提出物：{e("、".join(r.documents))}</div>' if r.documents else ""
        parts.append(
            f'<div class="mk-step"><div class="date{"" if r.date else " none"}">{e(date)}</div>'
            f'<div class="line"><div class="c{" fix" if fixed else ""}{" none" if not r.date else ""}"></div></div>'
            f'<div class="body"><div class="t">{e(r.label)}　{badge(r.who, "b-gray")}</div><div class="d">{e(r.date_note)}。{e(r.description)}</div>{docs}</div></div>'
        )
    st.markdown(f'<div class="mk-card">{"".join(parts)}</div>', unsafe_allow_html=True)


def fields_table(fields: list[dict]):
    mark = {"記入済": "", "要確認": badge("要確認", "b-yellow"), "未入力": badge("未入力", "b-red")}
    rows = "".join(f'<div class="mk-field"><div class="k">{e(f["label"])}</div><div class="v">{e(f["value"]) or "（空欄）"}</div><div>{mark[f["status"]]}</div></div>' for f in fields)
    st.markdown(f'<div class="mk-card soft">{rows}</div>', unsafe_allow_html=True)


def colony_summary(lines: list[str]):
    st.markdown('<div class="mk-card soft"><h4>コロニー情報</h4>' + "".join(f'<div style="font-size:13.5px;line-height:1.7">{e(l)}</div>' for l in lines) + "</div>", unsafe_allow_html=True)
