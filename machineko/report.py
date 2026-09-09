"""年次報告（市民面）。会話で活動状況を聞き取り、報告データにする。"""
from __future__ import annotations

from .profile import MunicipalityProfile

REPORT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reply": {"type": "string"},
        "report": {
            "type": ["object", "null"],
            "additionalProperties": False,
            "properties": {
                "cat_count": {"type": ["integer", "null"]},
                "ear_tipped_count": {"type": ["integer", "null"]},
                "surgeries": {"type": ["integer", "null"]},
                "summary": {"type": "string"},
            },
            "required": ["cat_count", "ear_tipped_count", "surgeries", "summary"],
        },
        "complete": {"type": "boolean"},
    },
    "required": ["reply", "report", "complete"],
}

REPORT_SYSTEM = """あなたは自治体の地域猫活動支援制度の事務担当者です。登録済みコロニーの年次報告を会話で受け付けます。
一次資料に報告項目の定めがあればそれに従い、無ければ次を集めてください：現在の頭数、耳カット済み（手術済み）頭数、この1年で手術した頭数、変化（新規流入・死亡・譲渡・苦情の有無）。
- 一度に聞くのは2項目まで。前回報告や登録時の数値と比べて変化を確認する。
- 必要な項目が揃ったら complete を true にし、report に整理した内容を入れ、reply で確認の要約を出す。
- 揃うまでは report を null にする。
- summary は事務的に2〜3文。情緒的な表現は使わない。"""


def report_turn(llm, profile: MunicipalityProfile, record: dict, history: list[dict]) -> dict:
    messages = list(history)
    ctx_text = (
        f"## 対象コロニー\nID: {record['id']}／{record['ward']} {record['location']}\n"
        f"登録時の頭数: {record.get('cat_count')}（耳カット済 {record.get('ear_tipped_count')}）\n"
        f"過去の報告: {record.get('reports') or 'なし'}\n\n## 会話\n"
    )
    messages[0] = {"role": "user", "content": ctx_text + messages[0]["content"]}
    return llm.chat_json(
        task="report",
        system=REPORT_SYSTEM,
        messages=messages,
        schema=REPORT_SCHEMA,
        corpus=profile.corpus(),
        ctx={"profile": profile, "record": record, "history": history},
    )


def build_report_docx(profile: MunicipalityProfile, record: dict, report: dict, date) -> bytes:
    """第5号様式 活動状況報告書。配布 DOCX が無い様式なので、要綱の様式に沿ってゼロから組む。"""
    import io

    from .documents import build_document

    colony = record.get("colony") or {}
    members = colony.get("members") or []
    rep = next((m for m in members if "代表" in (m.get("role") or "")), members[0] if members else {})
    y, m, d = date.year, date.month, date.day
    fields = [
        {"label": "提出日", "value": f"令和{y - 2018}年{m}月{d}日"},
        {"label": "住所", "value": rep.get("address", "")},
        {"label": "活動者氏名", "value": rep.get("name", "") or record.get("representative", "")},
        {"label": "電話", "value": rep.get("phone", "")},
        {"label": "登録地域名", "value": f"{record.get('ward', '')}{record.get('town', '')}"},
        {"label": "現在管理する猫の頭数", "value": f"{report.get('cat_count')}頭"},
        {"label": "現在管理する猫のうち避妊去勢手術済の猫の頭数", "value": f"{report.get('ear_tipped_count')}頭"},
        {"label": "その他、まちねこ活動に関する報告事項（効果、苦情対応の状況、課題、活動内容の変更等含む）", "value": f"この1年の手術 {report.get('surgeries')}頭。{report.get('summary', '')}"},
    ]
    doc = build_document("第５号様式（第１２条関係）　まちねこ活動状況報告書", "（宛先）京都市医療衛生センター長", fields, [],
                         footer="※ 第5号様式は配布 DOCX が無いため、要綱記載の様式に沿って自動生成しています。")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
