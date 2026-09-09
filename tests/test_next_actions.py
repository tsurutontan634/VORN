import datetime as dt

from machineko.next_actions import next_actions
from machineko.mock import _timeline_spec

SPEC = _timeline_spec()


def test_before_submit():
    a = next_actions(spec=SPEC, intake_complete=False, findings=None, forms_done=set(), record=None, deadlines=None, notified=False, surgery_form_done=False)
    assert a[0]["title"] == "聞き取りを終える"
    a = next_actions(spec=SPEC, intake_complete=True, findings={"findings": [], "ready_to_apply": True}, forms_done=set(), record=None, deadlines=None, notified=False, surgery_form_done=False)
    assert "第１号様式" in "".join(a[0]["docs"])


def test_after_registration_uses_spec_documents():
    rec = {"id": "K-1", "registered_date": "2026-09-09"}
    d = {"status": "登録済", "next_report_base": dt.date(2027, 9, 9), "next_report_due": dt.date(2027, 10, 9), "renewal_due": dt.date(2029, 9, 9), "renewal_open": dt.date(2029, 8, 10)}
    a = next_actions(spec=SPEC, intake_complete=True, findings={"findings": []}, forms_done={"registration", "plan"}, record=rec, deadlines=d, notified=False, surgery_form_done=False, today=dt.date(2026, 9, 10))
    titles = [x["title"] for x in a]
    assert any("周知" in t for t in titles) and any("第４号様式" in doc for x in a for doc in x["docs"])
    assert any(x["due"] == dt.date(2027, 10, 9) for x in a)


def test_renewal_window():
    rec = {"id": "K-1", "registered_date": "2023-09-25"}
    d = {"status": "更新待ち", "next_report_base": None, "next_report_due": None, "renewal_due": dt.date(2026, 9, 25), "renewal_open": dt.date(2026, 8, 26)}
    a = next_actions(spec=SPEC, intake_complete=True, findings={"findings": []}, forms_done=set(), record=rec, deadlines=d, notified=True, surgery_form_done=True, today=dt.date(2026, 9, 9))
    assert a[0]["level"] == "now" and "第２号様式" in "".join(a[0]["docs"])
