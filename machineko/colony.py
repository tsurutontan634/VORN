"""コロニー（猫の群れ）1件分の情報。聞き取りで埋まり、以降の全工程が参照する。"""
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
    ward: str = ""                         # 区
    location: str = ""                     # 活動場所（町名・目印）
    cat_count: int | None = None           # 現在の頭数
    ear_tipped_count: int | None = None    # 耳カット済み頭数
    kittens_present: bool | None = None
    feeding_site: str = ""                 # 餌場
    feeding_site_is_private: bool | None = None  # 正当な権原のある私有地か
    feeding_site_permission: str = ""      # 権原（自宅敷地、所有者の承諾など）
    feeding_time: str = ""                 # 餌やりの時間帯・片付け方
    toilet_site: str = ""                  # トイレ
    neighborhood_association: str = ""     # 町内会等の名称
    explained_date: str = ""               # 町内会へ説明した日 (YYYY-MM-DD)
    consent_obtained: bool | None = None   # 同意を得たか
    members: list[Member] = dataclasses.field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Colony":
        d = dict(d or {})
        members = [Member(**{k: v for k, v in m.items() if k in Member.__dataclass_fields__}) for m in d.pop("members", []) or []]
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(members=members, **known)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def merge(self, patch: dict[str, Any]) -> "Colony":
        """LLM が返した部分更新を取り込む。None は「未回答」なので上書きしない。"""
        d = self.to_dict()
        for k, v in (patch or {}).items():
            if v is None or k not in d:
                continue
            if k == "members":
                d["members"] = v
            else:
                d[k] = v
        return Colony.from_dict(d)

    def summary_lines(self) -> list[str]:
        def yn(v):
            return "—" if v is None else ("はい" if v else "いいえ")

        lines = [
            f"場所：{self.ward} {self.location}".strip(),
            f"頭数：{self.cat_count if self.cat_count is not None else '—'}（耳カット済み {self.ear_tipped_count if self.ear_tipped_count is not None else '—'}）",
            f"餌場：{self.feeding_site or '—'}／私有地：{yn(self.feeding_site_is_private)}／権原：{self.feeding_site_permission or '—'}",
            f"トイレ：{self.toilet_site or '—'}",
            f"町内会等：{self.neighborhood_association or '—'}／説明日：{self.explained_date or '—'}／同意：{yn(self.consent_obtained)}",
            f"活動者：{len(self.members)}名",
        ]
        for m in self.members:
            lines.append(f"　- {m.name or '(氏名未入力)'}｜地域住民：{yn(m.is_resident)}｜京都市民：{yn(m.is_kyoto_citizen)}｜{m.role}")
        return lines


COLONY_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "ward": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "cat_count": {"type": ["integer", "null"]},
        "ear_tipped_count": {"type": ["integer", "null"]},
        "kittens_present": {"type": ["boolean", "null"]},
        "feeding_site": {"type": ["string", "null"]},
        "feeding_site_is_private": {"type": ["boolean", "null"]},
        "feeding_site_permission": {"type": ["string", "null"]},
        "feeding_time": {"type": ["string", "null"]},
        "toilet_site": {"type": ["string", "null"]},
        "neighborhood_association": {"type": ["string", "null"]},
        "explained_date": {"type": ["string", "null"]},
        "consent_obtained": {"type": ["boolean", "null"]},
        "members": {
            "type": ["array", "null"],
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "is_resident": {"type": ["boolean", "null"]},
                    "is_kyoto_citizen": {"type": ["boolean", "null"]},
                    "role": {"type": "string"},
                    "phone": {"type": "string"},
                },
                "required": ["name", "address", "is_resident", "is_kyoto_citizen", "role", "phone"],
            },
        },
        "notes": {"type": ["string", "null"]},
    },
    "required": [
        "ward", "location", "cat_count", "ear_tipped_count", "kittens_present",
        "feeding_site", "feeding_site_is_private", "feeding_site_permission", "feeding_time",
        "toilet_site", "neighborhood_association", "explained_date", "consent_obtained",
        "members", "notes",
    ],
}
