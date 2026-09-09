"""様式の書類出力。

LLM がコロニー情報と一次資料（様式・記載例）から「項目名 → 記入内容」を作る。
コード側は、様式テンプレート DOCX があれば項目名で探して埋め、無ければ python-docx でゼロから組む。
様式の項目名はコードに固定しない（テンプレートと記載例から LLM が読む）。
"""
from __future__ import annotations

import datetime as dt
import io

from docx import Document
from docx.shared import Pt

from .colony import Colony
from .profile import MunicipalityProfile

FIELDS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "form_title": {"type": "string"},
        "addressed_to": {"type": "string"},
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "label": {"type": "string"},
                    "value": {"type": "string"},
                    "status": {"type": "string", "enum": ["記入済", "要確認", "未入力"]},
                },
                "required": ["label", "value", "status"],
            },
        },
        "notes_for_applicant": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["form_title", "addressed_to", "fields", "notes_for_applicant"],
}

FILL_SYSTEM = """あなたは自治体の地域猫活動支援制度の申請書類を代筆する事務担当者です。
一次資料の中の様式テンプレートと記載例に沿って、コロニー情報から各記入欄を埋めてください。
- fields の label は様式にある項目名をそのまま使い、様式の並び順に出す。
- 記載例の文体（簡潔・事務的）に合わせる。情緒的な表現は使わない。
- コロニー情報に無い欄は value を空にし status を「未入力」にする。推測で埋めない。
- 情報はあるが記載例と照らして確認が要るものは「要確認」にし、理由を notes_for_applicant に書く。
- 日付は「令和◯年◯月◯日」形式に直す。"""


def fill_form_fields(llm, profile: MunicipalityProfile, colony: Colony, form_key: str, apply_date: dt.date | None) -> dict:
    form = profile.forms.get(form_key, {})
    user = (
        f"様式：{form.get('label', form_key)}（テンプレートファイル：{form.get('template', '不明')}）\n"
        f"申請日：{apply_date.isoformat() if apply_date else '未定'}\n\n"
        "## コロニー情報\n" + colony.to_json()
    )
    return llm.json(
        task=f"fill_{form_key}",
        system=FILL_SYSTEM,
        user=user,
        schema=FIELDS_SCHEMA,
        corpus=profile.corpus(),
        ctx={"profile": profile, "colony": colony, "form_key": form_key, "apply_date": apply_date},
    )


# ---- DOCX 生成 ----

def _fill_template(template_path, fields: list[dict]) -> Document | None:
    """テンプレート DOCX の表から項目名を探し、右隣のセルに値を書く。見つからない項目は末尾に追記する。"""
    doc = Document(str(template_path))
    unmatched = []
    for f in fields:
        if not f["value"]:
            continue
        placed = False
        for table in doc.tables:
            for row in table.rows:
                cells = row.cells
                for i, c in enumerate(cells):
                    if f["label"] in c.text and i + 1 < len(cells):
                        target = cells[i + 1]
                        if target.text.strip() == "":
                            target.text = f["value"]
                            placed = True
                            break
                if placed:
                    break
            if placed:
                break
        if not placed:
            unmatched.append(f)
    if unmatched:
        doc.add_paragraph("（以下、様式内で対応欄を特定できなかった項目。手作業で転記してください）")
        for f in unmatched:
            doc.add_paragraph(f"{f['label']}：{f['value']}")
    return doc


def _build_from_scratch(form_title: str, addressed_to: str, fields: list[dict], notes: list[str], profile: MunicipalityProfile) -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.size = Pt(10.5)
    doc.add_heading(form_title, level=1)
    doc.add_paragraph(addressed_to)
    doc.add_paragraph("")
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    for f in fields:
        row = table.add_row().cells
        row[0].text = f["label"]
        row[1].text = f["value"] if f["value"] else ("　" if f["status"] == "未入力" else f["value"])
    if notes:
        doc.add_paragraph("")
        doc.add_paragraph("申請者への確認事項（提出前に削除してください）：")
        for n in notes:
            doc.add_paragraph(n, style="List Bullet")
    doc.add_paragraph("")
    doc.add_paragraph(f"※ このファイルは {profile.name} 配布の様式テンプレートが無い環境で自動生成した代替です。提出時は配布様式に転記してください。")
    return doc


def render_docx(profile: MunicipalityProfile, form_key: str, filled: dict) -> tuple[bytes, str]:
    """(docx bytes, 生成方法ラベル) を返す。"""
    template = profile.template_path(form_key)
    if template:
        doc = _fill_template(template, filled["fields"])
        how = f"配布様式 {template.name} に転記"
    else:
        doc = _build_from_scratch(filled["form_title"], filled["addressed_to"], filled["fields"], filled["notes_for_applicant"], profile)
        how = "様式テンプレート未配置のため python-docx で生成"
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue(), how
