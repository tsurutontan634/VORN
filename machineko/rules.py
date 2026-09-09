"""要綱照合。

1. extract_rules: 自治体の一次資料から、登録要件・活動条件・報告義務を規則リストとして抽出する。
2. check_colony: 抽出した規則にコロニー情報を照らし、不足・注意・OK を出す。
どちらも規則の中身はコード側に書かない。
"""
from __future__ import annotations

import json

from .colony import Colony
from .profile import MunicipalityProfile

RULES_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "category": {"type": "string", "enum": ["申請者要件", "活動場所", "地域合意", "管理方法", "提出書類", "登録後の義務", "期限", "その他"]},
                    "requirement": {"type": "string"},
                    "applies_when": {"type": "string"},
                    "source_file": {"type": "string"},
                    "source_quote": {"type": "string"},
                },
                "required": ["id", "category", "requirement", "applies_when", "source_file", "source_quote"],
            },
        }
    },
    "required": ["rules"],
}

FINDINGS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "level": {"type": "string", "enum": ["不足", "注意", "OK"]},
                    "rule_id": {"type": "string"},
                    "message": {"type": "string"},
                    "action": {"type": "string"},
                },
                "required": ["level", "rule_id", "message", "action"],
            },
        },
        "ready_to_apply": {"type": "boolean"},
    },
    "required": ["findings", "ready_to_apply"],
}

EXTRACT_SYSTEM = """あなたは自治体の地域猫活動支援制度の事務担当者です。
渡された一次資料（要綱・様式・記載例・市HPの抜粋）だけを根拠に、
「登録申請が受理されるために満たすべき条件」と「登録後に守るべき義務・期限」を規則として列挙してください。
- 各規則には必ず根拠となる資料名と、その資料からの短い引用を付ける。
- 資料に書かれていないことを一般常識で補わない。
- 同じ内容の重複は1つにまとめる。
- id は R1, R2, ... の連番。"""

CHECK_SYSTEM = """あなたは自治体の地域猫活動支援制度の事務担当者です。
規則リストとコロニー情報を照らし合わせ、申請前に直すべき点を判定してください。
- 「不足」：このままでは申請できない、または規則を満たしていない。
- 「注意」：条件付きで満たしている、または確認が必要。
- 「OK」：満たしている。
- 未回答の項目（null や空文字）は「不足」とし、何を確認すべきか action に書く。
- message は事務的に、様式番号や規則の内容を具体的に書く。情緒的な表現は使わない。
- ready_to_apply は「不足」が1件も無いときだけ true。"""


def extract_rules(llm, profile: MunicipalityProfile) -> list[dict]:
    out = llm.json(
        task="extract_rules",
        system=EXTRACT_SYSTEM,
        user=f"{profile.name}「{profile.program_name}」の規則を抽出してください。",
        schema=RULES_SCHEMA,
        corpus=profile.corpus(),
        ctx={"profile": profile},
    )
    return out["rules"]


def check_colony(llm, profile: MunicipalityProfile, rules: list[dict], colony: Colony) -> dict:
    user = (
        "## 規則リスト\n" + json.dumps(rules, ensure_ascii=False, indent=1)
        + "\n\n## コロニー情報\n" + colony.to_json()
        + "\n\n各規則について判定してください。"
    )
    return llm.json(
        task="check_colony",
        system=CHECK_SYSTEM,
        user=user,
        schema=FINDINGS_SCHEMA,
        ctx={"profile": profile, "rules": rules, "colony": colony},
    )
