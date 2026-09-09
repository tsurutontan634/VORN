"""高島市（基金型）プロファイルがモック経路で 1→7 通ることを確認する。"""
import datetime as dt
import json
from pathlib import Path

from machineko import documents, report, rules, schedule
from machineko.colony import Colony
from machineko.llm import LLM
from machineko.profile import load_profile
from machineko.registry import Registry


def test_takashima_end_to_end(tmp_path):
    p = load_profile("takashima")
    llm = LLM(mock=True)
    c = Colony.from_dict(json.loads(Path("demo/sample_colony_takashima.json").read_text(encoding="utf-8")))
    r = rules.extract_rules(llm, p)
    assert any("翌々月" in x["requirement"] for x in r) and all(x["source_file"].endswith(".md") for x in r)
    spec = schedule.extract_timeline_spec(llm, p)
    assert spec["application_window"]["ticket_month_offset"] == 2
    e = schedule.earliest_schedule(spec, dt.date(2026, 9, 9))
    assert e["valid_from"] == dt.date(2026, 11, 1) and e["delay_days"] == 30
    reg = Registry("takashima", path=tmp_path / "t.json")
    filled = {k: documents.fill_form_fields(llm, p, c, k, dt.date(2026, 9, 9)) for k, f in p.forms.items() if not f.get("after_registration")}
    rec = reg.submit_application(c.to_dict(), filled, dt.date(2026, 9, 9), spec)
    assert rec["kind"] == "ticket" and rec["ticket_valid_until"] == "2026-11-30"
    reg.register(rec["id"], dt.date(2026, 10, 25))
    hist = [{"role": "user", "content": "a"}]
    out = report.report_turn(llm, p, reg.get(rec["id"]), hist)
    hist += [{"role": "assistant", "content": out["reply"]}, {"role": "user", "content": "b"}]
    out = report.report_turn(llm, p, reg.get(rec["id"]), hist)
    assert out["complete"] and out["report"]["surgeries"] == 6
    reg.submit_report(rec["id"], {"date": "2026-11-20", **out["report"]})
    assert reg.deadlines(reg.get(rec["id"]), dt.date(2026, 12, 1))["status"] == "報告済"
    data = report.build_report_docx(p, reg.get(rec["id"]), out["report"], dt.date(2026, 11, 20), spec)
    assert data[:2] == b"PK"
