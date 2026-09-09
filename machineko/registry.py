"""登録コロニー台帳（自治体面のデータ）。

市民面で提出した申請・報告がここに入り、自治体面（医療衛生センター職員）が一覧・詳細で見る。
永続化は JSON 1ファイル。デモ用なので排他制御はしない。
状態は保存せず、日付と報告履歴から毎回計算する。
報告・更新の期限ルール（間隔・日数）は要綱から抽出した値を提出時に保存し、それを使う。
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

from .schedule import add_months, earliest_schedule

ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = ROOT / "demo"
DATA_DIR = ROOT / "data"

RULE_KEYS = ("annual_report_interval_months", "annual_report_window_days", "registration_validity_years", "renewal_window_days_before", "application_window")


def _d(s: str | None) -> dt.date | None:
    return dt.date.fromisoformat(s) if s else None


class Registry:
    def __init__(self, municipality_id: str = "kyoto", path: Path | None = None, seed: Path | None = None):
        self.path = path or DATA_DIR / f"registry_{municipality_id}.json"
        self.seed = seed or SEED_DIR / f"registry_seed_{municipality_id}.json"
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
        prefix = (self.all()[0]["id"][0] if self.all() else "K")
        nums = [int(c["id"].rsplit("-", 1)[1]) for c in self.all() if c["id"].startswith(f"{prefix}-{year}-")]
        n = max(nums, default=0) + 1
        members = colony.get("members") or []
        rep = next((m for m in members if "代表" in (m.get("role") or "")), members[0] if members else {})
        window = (spec or {}).get("application_window")
        rec = {
            "id": f"{prefix}-{year}-{n:03d}",
            "kind": "ticket" if window else "registration",
            "ward": colony.get("ward", ""),
            "town": colony.get("town", ""),
            "location": colony.get("location", ""),
            "cat_count": colony.get("cat_count"),
            "ear_tipped_count": colony.get("ear_tipped_count"),
            "applied_date": applied_date.isoformat(),
            "registered_date": None,
            "rules": {k: (spec or {}).get(k) for k in RULE_KEYS},
            "representative": rep.get("name", ""),
            "tickets": max((colony.get("cat_count") or 0) - (colony.get("ear_tipped_count") or 0), 0) if window else None,
            "documents": {k: {"form_title": v["form_title"], "fields": v["fields"]} for k, v in documents.items()},
            "reports": [],
            "colony": colony,
        }
        if window:
            e = earliest_schedule(spec, applied_date)
            rec["ticket_valid_from"] = e["valid_from"].isoformat()
            rec["ticket_valid_until"] = e["valid_until"].isoformat()
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
        """次の年次報告の基準日・期限、更新の満了日・提出開始日、状態を返す。"""
        today = today or dt.date.today()
        reg = _d(rec.get("registered_date"))
        rules = rec.get("rules") or {}
        if rec.get("kind") == "ticket":
            return Registry._ticket_deadlines(rec, today)
        interval = rules.get("annual_report_interval_months")
        window = rules.get("annual_report_window_days") or 0
        validity = rules.get("registration_validity_years")
        before = rules.get("renewal_window_days_before") or 0
        out = {"next_report_base": None, "next_report_due": None, "renewal_due": None, "renewal_open": None, "status": "申請中", "last_report": None}
        if not reg:
            return out
        if validity:
            out["renewal_due"] = add_months(reg, validity * 12)
            out["renewal_open"] = out["renewal_due"] - dt.timedelta(days=before)
        reports = sorted(rec.get("reports", []), key=lambda r: r["date"])
        out["last_report"] = _d(reports[-1]["date"]) if reports else None

        # 更新
        if out["renewal_due"]:
            if today > out["renewal_due"]:
                out["status"] = "期限超過"
                return out
            if today >= out["renewal_open"]:
                out["status"] = "更新待ち"
                return out
        if not interval:
            out["status"] = "登録済"
            return out
        # 年次報告：k 回目の基準日 = 登録日 + interval*k。報告が k-1 件あれば k 回目が次。
        k = len(reports) + 1
        base = add_months(reg, interval * k)
        due = base + dt.timedelta(days=window)
        if out["renewal_due"] and base >= out["renewal_due"]:
            # 更新年度は更新申請書で代替（報告の期限は立てない）
            out["status"] = "登録済"
            return out
        out["next_report_base"] = base
        out["next_report_due"] = due
        if today > due:
            out["status"] = "期限超過"
        elif today >= base:
            out["status"] = "報告待ち"
        elif out["last_report"] and (today - out["last_report"]).days <= (window or 30):
            out["status"] = "報告済"
        else:
            out["status"] = "登録済"
        return out

    @staticmethod
    def _ticket_deadlines(rec: dict, today: dt.date) -> dict:
        """チケット型：交付 → 有効月に実施 → 完了報告。未報告なら次回申請不可。"""
        vf, vu = _d(rec.get("ticket_valid_from")), _d(rec.get("ticket_valid_until"))
        reports = sorted(rec.get("reports", []), key=lambda r: r["date"])
        out = {"next_report_base": vf, "next_report_due": vu, "renewal_due": None, "renewal_open": None,
               "status": "申請中", "last_report": _d(reports[-1]["date"]) if reports else None}
        if not rec.get("registered_date"):
            return out
        if reports:
            out["status"] = "報告済"
        elif vf and today < vf:
            out["status"] = "交付済"
        elif vu and today > vu:
            out["status"] = "期限超過"
        else:
            out["status"] = "報告待ち"
        return out

    def rows(self, today: dt.date | None = None) -> list[dict]:
        rows = []
        for rec in self.all():
            d = self.deadlines(rec, today)
            rows.append({
                "ID": rec["id"],
                "区": rec["ward"],
                "活動地域": f"{rec.get('town', '')} {rec.get('location', '')}".strip(),
                "頭数": rec["cat_count"],
                "手術済": rec["ear_tipped_count"],
                "申請日": rec["applied_date"],
                "登録日" if rec.get("kind") != "ticket" else "交付日": rec.get("registered_date") or "—",
                "次回報告期限" if rec.get("kind") != "ticket" else "報告期限（有効月末）": d["next_report_due"].isoformat() if d["next_report_due"] else "—",
                "更新満了日" if rec.get("kind") != "ticket" else "チケット枚数": (d["renewal_due"].isoformat() if d["renewal_due"] else "—") if rec.get("kind") != "ticket" else rec.get("tickets"),
                "状態": d["status"],
            })
        order = {"期限超過": 0, "報告待ち": 1, "更新待ち": 2, "申請中": 3, "交付済": 4, "報告済": 5, "登録済": 6}
        return sorted(rows, key=lambda r: (order.get(r["状態"], 9), r["ID"]))
