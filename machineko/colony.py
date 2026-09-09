"""コロニー（猫の群れ）1件分の情報。聞き取りで埋まり、以降の全工程が参照する。

項目は京都市の第1号様式（登録申請書）・第6号様式（活動実施計画書）に必要なものを網羅する。
"""
from __future__ import annotations

import dataclasses
import json
from typing import Any


@dataclasses.dataclass
class Member:
    name: str = ""
    address: str = ""
    is_resident: bool | None = None      # 活動場所の地域住民か
    is_kyoto_citizen: bool | None = None  # 京都市民か
    role: str = ""                        # 代表 / 連絡担当 など
    phone: str = ""


@dataclasses.dataclass
class Colony:
    # 場所・猫
    ward: str = ""                         # 区
    town: str = ""                         # 町内（活動地域は町内会等単位が原則）
    location: str = ""                     # 目印（餌場周辺など）
    cat_count: int | None = None           # 現在管理する猫の頭数
    ear_tipped_count: int | None = None    # うち避妊去勢手術実施済（耳カット）
    kittens_present: bool | None = None
    # 管理方法
    feeding_site: str = ""                 # 餌場の場所
    feeding_sites_count: int | None = None # 餌やりを行う場所（か所）
    feeding_site_is_private: bool | None = None  # 正当な権原のある私有地か
    feeding_site_permission: str = ""      # 権原（自宅敷地、所有者の承諾など）
    feeding_time: str = ""                 # 餌やりを行う時間
    feeding_people: int | None = None      # 餌やりを行う人数
    toilet_site: str = ""                  # トイレの場所
    toilet_count: int | None = None        # トイレの設置数（か所）
    cleaning_time: str = ""                # ふんの清掃を行う時間
    cleaning_people: int | None = None     # ふんの清掃を行う人数
    complaint_contact: str = ""            # 苦情等の連絡先
    complaint_cases: str = ""              # 苦情対応事例
    issues: str = ""                       # 活動における問題点などその他参考事項
    # 地域合意
    neighborhood_association: str = ""     # 町内会等の名称
    association_rep_name: str = ""         # 町内会等の代表者 氏名
    association_rep_address: str = ""      # 同 住所
    association_rep_phone: str = ""        # 同 電話
    explained_date: str = ""               # 説明実施日 (YYYY-MM-DD)
    explained_by: str = ""                 # 説明の実施者
    consent_obtained: bool | None = None   # 町内会等の代表者の同意
    notify_methods: list[str] = dataclasses.field(default_factory=list)  # 周知方法（町内会への説明・回覧板・掲示板・投函・その他）
    notify_frequency_per_year: int | None = None  # 周知の頻度（年 回）
    # 活動者
    members: list[Member] = dataclasses.field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Colony":
        d = dict(d or {})
        members = [Member(**{k: v for k, v in m.items() if k in Member.__dataclass_fields__}) for m in d.pop("members", []) or []]
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        if known.get("notify_methods") is None:
            known["notify_methods"] = []
        return cls(members=members, **known)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def merge(self, patch: dict[str, Any]) -> "Colony":
        """LLM が返した部分更新を取り込む。None は「未回答」なので上書きしない。"""
        d = self.to_dict()
        for k, v in (patch or {}).items():
            if v is None or k not in d:
                continue
            d[k] = v
        return Colony.from_dict(d)

    def representative(self) -> Member | None:
        for m in self.members:
            if "代表" in (m.role or ""):
                return m
        return self.members[0] if self.members else None

    def summary_lines(self) -> list[str]:
        def yn(v):
            return "—" if v is None else ("はい" if v else "いいえ")

        def n(v):
            return "—" if v is None else str(v)

        lines = [
            f"活動地域：{self.ward} {self.town}（{self.location or '—'}）",
            f"頭数：{n(self.cat_count)}（手術済 {n(self.ear_tipped_count)}）／子猫：{yn(self.kittens_present)}",
            f"餌場：{self.feeding_site or '—'}（{n(self.feeding_sites_count)}か所／私有地：{yn(self.feeding_site_is_private)}／{self.feeding_site_permission or '—'}）",
            f"餌やり：{self.feeding_time or '—'}／{n(self.feeding_people)}人",
            f"トイレ：{self.toilet_site or '—'}（{n(self.toilet_count)}か所）／清掃：{self.cleaning_time or '—'}／{n(self.cleaning_people)}人",
            f"苦情連絡先：{self.complaint_contact or '—'}",
            f"町内会等：{self.neighborhood_association or '—'}／代表者：{self.association_rep_name or '—'}",
            f"説明実施日：{self.explained_date or '—'}（{self.explained_by or '—'}）／代表者同意：{yn(self.consent_obtained)}",
            f"周知方法：{'・'.join(self.notify_methods) or '—'}／年{n(self.notify_frequency_per_year)}回",
            f"活動者：{len(self.members)}名",
        ]
        for m in self.members:
            lines.append(f"　- {m.name or '(氏名未入力)'}｜地域住民：{yn(m.is_resident)}｜京都市民：{yn(m.is_kyoto_citizen)}｜{m.role}")
        return lines


def _s():
    return {"type": ["string", "null"]}


def _i():
    return {"type": ["integer", "null"]}


def _b():
    return {"type": ["boolean", "null"]}


_PROPS = {
    "ward": _s(), "town": _s(), "location": _s(),
    "cat_count": _i(), "ear_tipped_count": _i(), "kittens_present": _b(),
    "feeding_site": _s(), "feeding_sites_count": _i(), "feeding_site_is_private": _b(), "feeding_site_permission": _s(),
    "feeding_time": _s(), "feeding_people": _i(),
    "toilet_site": _s(), "toilet_count": _i(), "cleaning_time": _s(), "cleaning_people": _i(),
    "complaint_contact": _s(), "complaint_cases": _s(), "issues": _s(),
    "neighborhood_association": _s(), "association_rep_name": _s(), "association_rep_address": _s(), "association_rep_phone": _s(),
    "explained_date": _s(), "explained_by": _s(), "consent_obtained": _b(),
    "notify_methods": {"type": ["array", "null"], "items": {"type": "string"}},
    "notify_frequency_per_year": _i(),
    "members": {
        "type": ["array", "null"],
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "address": {"type": "string"},
                "is_resident": _b(),
                "is_kyoto_citizen": _b(),
                "role": {"type": "string"},
                "phone": {"type": "string"},
            },
            "required": ["name", "address", "is_resident", "is_kyoto_citizen", "role", "phone"],
        },
    },
    "notes": _s(),
}

COLONY_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": _PROPS,
    "required": list(_PROPS.keys()),
}
