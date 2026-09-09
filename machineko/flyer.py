"""地域へのお知らせ（周知チラシ）。参考様式に沿った文面を LLM が作る。"""
from __future__ import annotations

from .colony import Colony
from .profile import MunicipalityProfile

FLYER_SYSTEM = """あなたは自治体の地域猫活動支援制度の事務担当者です。
一次資料にある「地域へのお知らせ」の参考様式に沿って、周知チラシの本文を作ってください。
- 目的（不妊去勢手術のための一時的な捕獲）、期間、場所、連絡先、飼い猫への注意（首輪など）、自治体の事業であることを含める。
- 情緒的な表現（かわいそう、命を救う など）は使わない。事実と依頼事項だけを書く。
- 空欄にすべき日付は「令和　年　月　日」のように残す。
- Markdown ではなくプレーンテキストで、A4一枚に収まる分量にする。"""


def generate_flyer(llm, profile: MunicipalityProfile, colony: Colony, trap_period: str) -> str:
    user = (
        f"捕獲予定期間：{trap_period or '未定'}\n"
        f"自治体窓口：{profile.office}（{'／'.join(profile.contacts)}）\n\n"
        "## コロニー情報\n" + colony.to_json()
    )
    return llm.text(
        task="flyer",
        system=FLYER_SYSTEM,
        user=user,
        corpus=profile.corpus(),
        ctx={"profile": profile, "colony": colony, "trap_period": trap_period},
    )
