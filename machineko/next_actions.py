"""市民面の先頭に出す「次にやること」。

要綱から抽出した工程（timeline spec）と、台帳の状態、画面の進み具合から、次の1〜3件を組み立てる。
規則の中身（様式名・期限日数）は spec と台帳の rules から取り、ここには書かない。
"""
from __future__ import annotations

import datetime as dt


def _docs(spec: dict | None, key: str) -> list[str]:
    for s in (spec or {}).get("steps", []):
        if s["key"] == key:
            return list(s.get("documents", []))
    return []


def _label(spec: dict | None, key: str, default: str) -> str:
    for s in (spec or {}).get("steps", []):
        if s["key"] == key:
            return s["label"]
    return default


def next_actions(*, spec: dict | None, intake_complete: bool, findings: dict | None, forms_done: set[str],
                 record: dict | None, deadlines: dict | None, notified: bool, surgery_form_done: bool,
                 today: dt.date | None = None) -> list[dict]:
    """各要素: {"title", "due"(date|None), "docs"(list), "note", "level"("now"|"soon"|"wait"|"late")}"""
    today = today or dt.date.today()
    out: list[dict] = []

    if not intake_complete:
        out.append({"title": "聞き取りを終える", "due": None, "docs": [], "note": "様式に必要な項目を会話で集めます（1. 聞き取り）", "level": "now"})
        return out
    if findings is None:
        out.append({"title": "要綱に照らして不足を確認する", "due": None, "docs": [], "note": "2. 要綱照合", "level": "now"})
        return out
    lacking = [f for f in findings.get("findings", []) if f["level"] == "不足"]
    if lacking:
        out.append({"title": f"不足 {len(lacking)} 件を解消する", "due": None, "docs": [], "note": "／".join(f["action"] or f["message"] for f in lacking[:3]), "level": "now"})
        return out
    if record is None:
        need = _docs(spec, "apply") or ["登録申請書", "活動実施計画書"]
        done = {"registration", "plan"} <= forms_done
        note = "3. 書類出力で作成し、提出ボタンで台帳に載せます" if not done else "2様式は作成済み。提出ボタンを押してください"
        due = None
        if spec and spec.get("application_window"):
            from .schedule import earliest_schedule

            e = earliest_schedule(spec, today)
            due = e["apply"] if e["apply"] > today else None
            note += f"。今出すと有効期間 {e['valid_from']} 〜 {e['valid_until']}、この受付を逃すと +{e['delay_days']} 日"
        out.append({"title": _label(spec, "apply", "申請書類を提出する"), "due": due, "docs": need, "note": note, "level": "now"})
        return out
    if not record.get("registered_date"):
        out.append({"title": _label(spec, "review", "審査・現地調査を待つ"), "due": None, "docs": [], "note": f"台帳ID {record['id']}。日程は自治体から連絡があります", "level": "wait"})
        return out

    # 登録後
    if not notified:
        out.append({"title": _label(spec, "notify", "地域へ周知する"), "due": None, "docs": _docs(spec, "notify"), "note": "捕獲の前に行います（4. 周知チラシ）", "level": "now"})
    if not surgery_form_done:
        docs = _docs(spec, "trap")
        out.append({"title": _label(spec, "trap", "手術を申請する"), "due": None, "docs": docs, "note": "3. 書類出力で作成。手術日時は自治体から通知されます", "level": "now" if notified else "soon"})
    d = deadlines or {}
    if d.get("status") == "期限超過":
        out.append({"title": "期限を過ぎています。至急提出", "due": d.get("next_report_due") or d.get("renewal_due"), "docs": _docs(spec, "annual_report") if d.get("next_report_due") else _docs(spec, "renewal"), "note": "自治体に連絡してください", "level": "late"})
    elif d.get("renewal_open") and today >= d["renewal_open"]:
        out.append({"title": _label(spec, "renewal", "登録を更新する"), "due": d["renewal_due"], "docs": _docs(spec, "renewal"), "note": f"受付期間 {d['renewal_open']} 〜 {d['renewal_due']}", "level": "now"})
    elif d.get("next_report_base"):
        level = "now" if today >= d["next_report_base"] else "soon"
        out.append({"title": _label(spec, "annual_report", "活動状況を報告する"), "due": d["next_report_due"], "docs": _docs(spec, "annual_report"),
                    "note": f"基準日 {d['next_report_base']}（7. 年次報告）", "level": level})
    if d.get("renewal_due") and not any(a["level"] == "now" and "更新" in a["title"] for a in out):
        out.append({"title": "登録の満了日", "due": d["renewal_due"], "docs": [], "note": f"更新の受付は {d.get('renewal_open')} から", "level": "soon"})
    return out[:4]
