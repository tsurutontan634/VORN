import datetime as dt

from machineko import schedule


def _spec(interval=12, validity=3):
    return {
        "steps": [{"key": k, "label": k, "who_decides_date": "申請者", "description": "", "documents": [], "source_quote": ""} for k in schedule.STEP_KEYS],
        "annual_report_interval_months": interval,
        "annual_report_window_days": 30,
        "registration_validity_years": validity,
        "renewal_window_days_before": 30,
        "renewal_note": "",
        "termination_note": "",
        "other_deadlines": [{"label": "廃止届", "condition": "やめるとき", "source_quote": ""}],
    }


def test_add_months_clamps_day():
    assert schedule.add_months(dt.date(2027, 1, 31), 1) == dt.date(2027, 2, 28)
    assert schedule.add_months(dt.date(2026, 10, 20), 12) == dt.date(2027, 10, 20)


def test_timeline_from_register_date():
    rows = schedule.build_timeline(_spec(), schedule.Anchors(register=dt.date(2026, 10, 20)))
    reports = [r for r in rows if r.key == "annual_report"]
    assert [r.date for r in reports] == [dt.date(2027, 11, 19), dt.date(2028, 11, 19)]  # 同月日 + 30日
    renewal = next(r for r in rows if r.key == "renewal")
    assert renewal.date == dt.date(2029, 10, 20)


def test_timeline_without_register_date_has_no_computed_dates():
    rows = schedule.build_timeline(_spec(), schedule.Anchors())
    assert all(r.date is None for r in rows)


def test_spec_without_numbers_does_not_invent():
    rows = schedule.build_timeline(_spec(interval=None, validity=None), schedule.Anchors(register=dt.date(2026, 1, 1)))
    assert next(r for r in rows if r.key == "annual_report").date is None
    assert "記載なし" in next(r for r in rows if r.key == "renewal").date_note
