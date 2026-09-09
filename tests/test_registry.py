import datetime as dt

from machineko.registry import Registry


def _reg(tmp_path):
    return Registry("kyoto", path=tmp_path / "registry.json")


def test_seed_statuses(tmp_path):
    r = _reg(tmp_path)
    st = {row["ID"]: row["状態"] for row in r.rows(dt.date(2026, 9, 9))}
    assert st["K-2026-009"] == "申請中"
    assert st["K-2025-041"] == "期限超過"
    assert st["K-2024-017"] == "報告待ち"
    assert st["K-2023-102"] == "更新待ち"


def test_apply_register_report_flow(tmp_path):
    r = _reg(tmp_path)
    today = dt.date(2026, 9, 9)
    spec = {"annual_report_interval_months": 12, "annual_report_window_days": 30, "registration_validity_years": 3, "renewal_window_days_before": 30}
    rec = r.submit_application({"ward": "左京区", "location": "x", "cat_count": 11, "ear_tipped_count": 2, "members": [{"name": "山田"}]},
                               {"registration": {"form_title": "第1号様式", "fields": []}}, today, spec)
    assert rec["id"] == "K-2026-010" and r.deadlines(rec, today)["status"] == "申請中"
    r.register(rec["id"], today)
    d = r.deadlines(r.get(rec["id"]), today)
    assert d["status"] == "登録済" and d["next_report_base"] == dt.date(2027, 9, 9) and d["next_report_due"] == dt.date(2027, 10, 9)
    assert d["renewal_due"] == dt.date(2029, 9, 9) and d["renewal_open"] == dt.date(2029, 8, 10)
    # 同月日を過ぎると報告待ち、30日を過ぎると超過
    assert r.deadlines(r.get(rec["id"]), dt.date(2027, 9, 9))["status"] == "報告待ち"
    assert r.deadlines(r.get(rec["id"]), dt.date(2027, 10, 10))["status"] == "期限超過"
    r.submit_report(rec["id"], {"date": "2027-09-15", "cat_count": 12, "ear_tipped_count": 12, "surgeries": 10, "summary": "s"})
    d = r.deadlines(r.get(rec["id"]), dt.date(2027, 9, 16))
    assert d["status"] == "報告済" and d["next_report_base"] == dt.date(2028, 9, 9)
    # 更新年度は更新待ち／満了日を過ぎると超過
    assert r.deadlines(r.get(rec["id"]), dt.date(2029, 8, 15))["status"] == "更新待ち"
    assert r.deadlines(r.get(rec["id"]), dt.date(2029, 9, 10))["status"] == "期限超過"
    # 永続化
    assert Registry("kyoto", path=tmp_path / "registry.json").get(rec["id"])["cat_count"] == 12


def test_ticket_type(tmp_path):
    r = Registry("takashima", path=tmp_path / "t.json")
    st = {row["ID"]: row["状態"] for row in r.rows(dt.date(2026, 9, 9))}
    assert st == {"T-2026-003": "期限超過", "T-2026-005": "報告待ち", "T-2026-007": "申請中"}
    spec = {"application_window": {"from_day": 6, "to_day": None, "ticket_month_offset": 2, "valid_months": 1, "max_tickets": None, "report_required_before_next": True, "source_quote": ""}}
    rec = r.submit_application({"town": "x", "cat_count": 6, "ear_tipped_count": 0, "members": [{"name": "森"}]}, {}, dt.date(2026, 9, 9), spec)
    assert rec["kind"] == "ticket" and rec["tickets"] == 6 and rec["ticket_valid_from"] == "2026-11-01"
    r.register(rec["id"], dt.date(2026, 10, 20))
    assert r.deadlines(r.get(rec["id"]), dt.date(2026, 10, 25))["status"] == "交付済"
    assert r.deadlines(r.get(rec["id"]), dt.date(2026, 11, 10))["status"] == "報告待ち"
    r.submit_report(rec["id"], {"date": "2026-11-20", "cat_count": 6, "ear_tipped_count": 6, "surgeries": 6, "summary": "s"})
    assert r.deadlines(r.get(rec["id"]), dt.date(2026, 12, 5))["status"] == "報告済"
