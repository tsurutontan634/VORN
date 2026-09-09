import datetime as dt

from machineko.registry import Registry


def _reg(tmp_path):
    return Registry(path=tmp_path / "registry.json")


def test_seed_statuses(tmp_path):
    r = _reg(tmp_path)
    st = {row["ID"]: row["状態"] for row in r.rows(dt.date(2026, 9, 9))}
    assert st["K-2026-009"] == "申請中"
    assert st["K-2025-041"] == "期限超過"
    assert st["K-2023-102"] == "報告待ち"
    assert st["K-2024-017"] == "登録済"


def test_apply_register_report_flow(tmp_path):
    r = _reg(tmp_path)
    today = dt.date(2026, 9, 9)
    spec = {"annual_report_interval_months": 12, "registration_validity_years": 3}
    rec = r.submit_application({"ward": "左京区", "location": "x", "cat_count": 11, "ear_tipped_count": 2, "members": [{"name": "山田"}]},
                               {"registration": {"form_title": "第1号様式", "fields": []}}, today, spec)
    assert rec["id"] == "K-2026-010" and r.deadlines(rec, today)["status"] == "申請中"
    r.register(rec["id"], today)
    d = r.deadlines(r.get(rec["id"]), today)
    assert d["status"] == "登録済" and d["next_report_due"] == dt.date(2027, 9, 9) and d["renewal_due"] == dt.date(2029, 9, 9)
    # 1年後、期限直前に報告
    assert r.deadlines(r.get(rec["id"]), dt.date(2027, 8, 1))["status"] == "報告待ち"
    r.submit_report(rec["id"], {"date": "2027-08-05", "cat_count": 12, "ear_tipped_count": 12, "surgeries": 10, "summary": "s"})
    d = r.deadlines(r.get(rec["id"]), dt.date(2027, 8, 6))
    assert d["status"] == "報告済" and d["next_report_due"] == dt.date(2028, 9, 9)
    # 報告なしで期限を過ぎると超過
    assert r.deadlines(r.get(rec["id"]), dt.date(2028, 9, 10))["status"] == "期限超過"
    # 永続化
    assert Registry(path=tmp_path / "registry.json").get(rec["id"])["cat_count"] == 12
