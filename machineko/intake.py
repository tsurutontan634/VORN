"""聞き取り。会話でコロニー情報を集め、Colony を少しずつ埋める。"""
from __future__ import annotations

from .colony import COLONY_JSON_SCHEMA, Colony
from .profile import MunicipalityProfile

INTAKE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reply": {"type": "string"},
        "colony_patch": COLONY_JSON_SCHEMA,
        "complete": {"type": "boolean"},
    },
    "required": ["reply", "colony_patch", "complete"],
}

INTAKE_SYSTEM = """あなたは自治体の地域猫活動支援制度の事務担当者です。申請に必要な情報を会話で集めます。
対象は「町内会等への説明と同意がすでに済んでいる」個人ボランティアです。

集める項目（一次資料の様式・記載例に必要なもの）：
場所（区・町名・目印）、頭数、耳カット済みの頭数、子猫の有無、餌場とその土地の権原（私有地か・誰の承諾か）、
餌やりの時間と片付け、トイレの場所、町内会等の名称・説明した日付・同意の有無、
活動者（氏名・住所・地域住民か・京都市民か・役割・電話）。

進め方：
- 一度に聞くのは2〜3項目まで。すでに分かっている項目は聞き直さない。
- ユーザーの発言から読み取れた項目だけを colony_patch に入れる。分からない項目は null。members は全員分をまとめて返す。
- colony_patch は毎回必ず出す（新しい情報が無ければ {}）。氏名だけ・場所だけのように不完全でも、その時点で分かった分を colony_patch に入れる。次の発言で足りない分を補う。
- 出力は reply・colony_patch・complete の3項目を持つ JSON オブジェクト。
- 必須項目がすべて埋まったら complete を true にし、reply で確認の要約を出す。
- 捕獲のやり方、町内会の説得、里親探し、子猫の育て方を聞かれたら「この窓口の範囲外」と短く伝えて本題に戻す。
- 情緒的な表現は使わない。事務的に、短く。"""


def intake_turn(llm, profile: MunicipalityProfile, colony: Colony, history: list[dict]) -> dict:
    """history は [{"role": "user"|"assistant", "content": str}, ...]。最後は user。"""
    messages = list(history)
    # 現在の Colony を先頭 user メッセージに添えて、聞き直しを防ぐ
    messages[0] = {"role": "user", "content": "## 現在までに分かっている情報\n" + colony.to_json() + "\n\n## 会話\n" + messages[0]["content"]}
    return llm.chat_json(
        task="intake",
        system=INTAKE_SYSTEM,
        messages=messages,
        schema=INTAKE_SCHEMA,
        corpus=profile.corpus(),
        ctx={"profile": profile, "colony": colony, "history": history},
    )
