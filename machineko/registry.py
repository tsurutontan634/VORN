"""登録コロニー台帳（自治体面のデータ）。

市民面で提出した申請・報告がここに入り、自治体面（医療衛生センター職員）が一覧・詳細で見る。
永続化は JSON 1ファイル。デモ用なので排他制御はしない。
状態は保存せず、日付と報告履歴から毎回計算する。
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

from .schedule import add_months

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "demo" / "registry_seed.json"
DATA = ROOT / "data" / "registry.json"

REPORT_LEAD_DAYS = 60   # 期限の何日前から「報告待ち」にするか（運用上の設定値。要綱の値ではない）


def _d(s: str | None) -> dt.date | None:
    return dt.date.fromisoformat(s) if s else None


class Registry:
    def __init__(self, path: Path = DATA, seed: Path = SEED):
        self.path = path
        self.seed = seed
        if not self.path.exists():
            self.reset()
        self._load()

    # ---- 永続化 ----
    def _load(self):
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def reset(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(self.seed, self.path)
        self._load()

    # ---- 参照 ----
    def all(self) -> list[dict]:
        return self.data["colonies"]

    def get(self, cid: str) -> dict | None:
        return next((c for c in self.all() if c["id"] == cid), None)

    # ---- 市民面からの操作 ----
    def submit_application(self, colony: dict, documents: dict, applied_date: dt.date, spec: dict | None) -> dict:
        year = applied_date.year
        nums = [int(c["id"].rsplit("-", 1)[1]) for c in self.all() if c["id"].startswith(f"K-{year}-")]
        n = max(nums, default=0) + 1
        members = colony.get("members") or []
        rec = {
            "id": f"K-{year}-{n:03d}",
            "ward": colony.get("ward", ""),
            "location": colony.get("location", ""),
            "cat_count": colony.get("cat_count"),
            "ear_tipped_count": colony.get("ear_tipped_count"),
            "applied_date": applied_date.isoformat(),
            "registered_date": None,
            "annual_report_interval_months": (spec or {}).get("annual_report_interval_months"),
            "registration_validity_years": (spec or {}).get("registration_validity_years"),
            "representative": members[0].get("name", "") if members else "",
            "documents": {k: {"form_title": v["form_title"], "fields": v["fields"]} for k, v in documents.items()},
            "reports": [],
            "colony": colony,
        }
        self.data["colonies"].append(rec)
        self._save()
        return rec

    def submit_report(self, cid: str, report: dict) -> dict:
        rec = self.get(cid)
        rec["reports"].append(report)
        if report.get("cat_count") is not None:
            rec["cat_count"] = report["cat_count"]
        if report.get("ear_tipped_count") is not None:
            rec["ear_tipped_count"] = report["ear_tipped_count"]
        self._save()
        return rec

    # ---- 自治体面からの操作 ----
    def register(self, cid: str, registered_date: dt.date) -> dict:
        rec = self.get(cid)
        rec["registered_date"] = registered_date.isoformat()
        self._save()
        return rec

    # ---- 状態計算 ----
    @staticmethod
    def deadlines(rec: dict, today: dt.date | None = None) -> dict:
        """次の年次報告期限・更新期限・状態を返す。"""
        today = today or dt.date.today()
        reg = _d(rec.get("registered_date"))
        interval = rec.get("annual_report_interval_months")
        validity = rec.get("registration_validity_years")
        out = {"next_report_due": None, "renewal_due": None, "status": "申請中", "last_report": None}
        if not reg:
            return out
        if validity:
            out["renewal_due"] = add_months(reg, validity * 12)
        reports = sorted(rec.get("reports", []), key=lambda r: r["date"])
        out["last_report"] = _d(reports[-1]["date"]) if reports else None
        if not interval:
            out["status"] = "登録済"
            return out
        # 報告サイクル k 回目の期限 = 登録日 + interval*k。報告が k 件あれば k+1 回目が次の期限。
        k = len(reports) + 1
        due = add_months(reg, interval * k)
        limit = out["renewal_due"] or due
        if due > limit:
            due = limit
        out["next_report_due"] = due
        if out["renewal_due"] and today > out["renewal_due"]:
            out["status"] = "期限超過"
        elif today > due:
            out["status"] = "期限超過"
        elif reports and (today - out["last_report"]).days <= REPORT_LEAD_DAYS:
            out["status"] = "報告済"
        elif (due - today).days <= REPORT_LEAD_DAYS:
            out["status"] = "報告待ち"
        else:
            out["status"] = "登録済"
        return out

    def rows(self, today: dt.date | None = None) -> list[dict]:
        rows = []
        for rec in self.all():
            d = self.deadlines(rec, today)
            rows.append({
                "ID": rec["id"],
                "区": rec["ward"],
                "場所": rec["location"],
                "頭数": rec["cat_count"],
                "耳カット済": rec["ear_tipped_count"],
                "申請日": rec["applied_date"],
                "登録日": rec.get("registered_date") or "—",
                "次回報告期限": d["next_report_due"].isoformat() if d["next_report_due"] else "—",
                "更新期限": d["renewal_due"].isoformat() if d["renewal_due"] else "—",
                "状態": d["status"],
            })
        order = {"期限超過": 0, "報告待ち": 1, "申請中": 2, "報告済": 3, "登録済": 4}
        return sorted(rows, key=lambda r: (order.get(r["状態"], 9), r["ID"]))
