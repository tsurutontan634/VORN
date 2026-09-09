"""日程表とリマインド。

LLM は一次資料から「工程の並び」「誰が日程を決めるか」「登録日から数えた期限」を抽出する。
日付の計算はコード側で行う（LLM に日付計算をさせない）。
"""
from __future__ import annotations

import dataclasses
import datetime as dt

from .profile import MunicipalityProfile

STEP_KEYS = ["apply", "review", "register", "notify", "trap", "surgery", "return", "annual_report", "renewal"]

TIMELINE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "key": {"type": "string", "enum": STEP_KEYS},
                    "label": {"type": "string"},
                    "who_decides_date": {"type": "string", "enum": ["申請者", "自治体", "個別調整", "規則で固定"]},
                    "description": {"type": "string"},
                    "documents": {"type": "array", "items": {"type": "string"}},
                    "source_quote": {"type": "string"},
                },
                "required": ["key", "label", "who_decides_date", "description", "documents", "source_quote"],
            },
        },
        "annual_report_interval_months": {"type": ["integer", "null"]},
        "registration_validity_years": {"type": ["integer", "null"]},
        "renewal_note": {"type": "string"},
        "termination_note": {"type": "string"},
        "other_deadlines": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "label": {"type": "string"},
                    "condition": {"type": "string"},
                    "source_quote": {"type": "string"},
                },
                "required": ["label", "condition", "source_quote"],
            },
        },
    },
    "required": ["steps", "annual_report_interval_months", "registration_validity_years", "renewal_note", "termination_note", "other_deadlines"],
}

TIMELINE_SYSTEM = """あなたは自治体の地域猫活動支援制度の事務担当者です。
一次資料から、登録申請から更新までの工程と期限を抽出してください。
- steps は apply（申請提出）→ review（審査・現地調査）→ register（登録）→ notify（地域への周知）→ trap（捕獲）→ surgery（センター持込・手術）→ return（元の場所へ戻す）→ annual_report（年次報告）→ renewal（更新）の順。
- who_decides_date：申請者が決めるもの／自治体が決めるもの／個別調整／規則で固定、を資料から判断する。
- 資料に日数・期間が書かれていないものは description に「資料に記載なし」と明記し、数字を作らない。
- annual_report_interval_months と registration_validity_years は資料に明記があるときだけ数字を入れ、無ければ null。
- other_deadlines には廃止届・変更届など、条件付きで発生する提出物を入れる。"""


def extract_timeline_spec(llm, profile: MunicipalityProfile) -> dict:
    return llm.json(
        task="timeline_spec",
        system=TIMELINE_SYSTEM,
        user=f"{profile.name}「{profile.program_name}」の工程と期限を抽出してください。",
        schema=TIMELINE_SCHEMA,
        corpus=profile.corpus(),
        ctx={"profile": profile},
    )


@dataclasses.dataclass
class TimelineRow:
    key: str
    label: str
    date: dt.date | None
    date_note: str      # 「予定」「登録日＋1年」「センターと調整」など
    who: str
    description: str
    documents: list[str]


@dataclasses.dataclass
class Anchors:
    """ユーザーが入力・調整する基準日。None は未定。"""
    apply: dt.date | None = None
    register: dt.date | None = None
    notify: dt.date | None = None
    trap: dt.date | None = None
    surgery: dt.date | None = None
    return_: dt.date | None = None


def add_months(d: dt.date, months: int) -> dt.date:
    y, m = divmod(d.month - 1 + months, 12)
    y += d.year
    m += 1
    leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    dim = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return dt.date(y, m, min(d.day, dim))


def build_timeline(spec: dict, anchors: Anchors) -> list[TimelineRow]:
    interval = spec.get("annual_report_interval_months")
    validity = spec.get("registration_validity_years")
    steps = {s["key"]: s for s in spec.get("steps", [])}

    def mk(key: str, date: dt.date | None, note: str) -> TimelineRow:
        s = steps.get(key, {"label": key, "who_decides_date": "", "description": "資料に記載なし", "documents": []})
        return TimelineRow(key, s["label"], date, note, s["who_decides_date"], s["description"], list(s.get("documents", [])))

    rows = [
        mk("apply", anchors.apply, "申請予定日" if anchors.apply else "未定"),
        mk("review", None, "自治体が実施（日程は自治体から連絡）"),
        mk("register", anchors.register, "登録日" if anchors.register else "未定（登録通知待ち）"),
        mk("notify", anchors.notify, "周知予定日" if anchors.notify else "登録後に設定"),
        mk("trap", anchors.trap, "捕獲予定日" if anchors.trap else "周知後に設定"),
        mk("surgery", anchors.surgery, "センターと調整済み" if anchors.surgery else "センターと個別調整"),
        mk("return", anchors.return_, "リターン予定日" if anchors.return_ else "手術後に設定"),
    ]

    base = anchors.register
    if interval and base:
        limit_months = (validity or 3) * 12
        months, n = interval, 1
        while months < limit_months:
            rows.append(mk("annual_report", add_months(base, months), f"登録日＋{months}か月（{n}回目）"))
            months += interval
            n += 1
    else:
        rows.append(mk("annual_report", None, "登録日が決まると自動計算" if interval else "資料に間隔の記載なし"))
    if validity and base:
        rows.append(mk("renewal", add_months(base, validity * 12), f"登録日＋{validity}年（有効期限）"))
    else:
        rows.append(mk("renewal", None, "登録日が決まると自動計算" if validity else "資料に有効期間の記載なし"))
    return rows


def build_reminders(spec: dict, rows: list[TimelineRow], today: dt.date | None = None) -> list[dict]:
    """期限のリマインド一覧。日付のあるものは残日数付き、条件付きのものは条件を表示。"""
    today = today or dt.date.today()
    out = []
    for r in rows:
        if r.key in ("annual_report", "renewal") and r.date:
            out.append({
                "label": r.label,
                "date": r.date.isoformat(),
                "days_left": (r.date - today).days,
                "note": r.date_note,
                "lead_days": 60 if r.key == "renewal" else 30,
            })
    for d in spec.get("other_deadlines", []):
        out.append({"label": d["label"], "date": None, "days_left": None, "note": d["condition"], "lead_days": None})
    return out
