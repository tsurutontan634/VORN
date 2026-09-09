"""モック経路で 1→6 が通ることを確認する。APIキー不要。"""
import datetime as dt
import json
from pathlib import Path

from machineko import documents, flyer, intake, rules, schedule
from machineko.colony import Colony
from machineko.llm import LLM
from machineko.profile import load_profile


def test_end_to_end_mock():
    p = load_profile("kyoto")
    llm = LLM(mock=True)
    c = Colony.from_dict(json.loads(Path("demo/sample_colony.json").read_text(encoding="utf-8")))

    r = rules.extract_rules(llm, p)
    assert all({"id", "requirement", "source_file", "source_quote"} <= set(x) for x in r)
    f = rules.check_colony(llm, p, r, c)
    assert f["ready_to_apply"] is True

    # 地域住民を1名に減らすと不足が出る
    c2 = Colony.from_dict({**c.to_dict(), "members": c.to_dict()["members"][:1]})
    assert rules.check_colony(llm, p, r, c2)["ready_to_apply"] is False

    for key in p.forms:
        filled = documents.fill_form_fields(llm, p, c, key, dt.date(2026, 9, 15))
        data, how = documents.render_docx(p, key, filled)
        assert data[:2] == b"PK"

    assert "首輪" in flyer.generate_flyer(llm, p, c, "")

    spec = schedule.extract_timeline_spec(llm, p)
    rows = schedule.build_timeline(spec, schedule.Anchors(register=dt.date(2026, 10, 20)))
    assert any(x.key == "renewal" and x.date for x in rows)


def test_intake_mock_completes():
    p = load_profile("kyoto")
    llm = LLM(mock=True)
    c = Colony()
    hist = []
    for i in range(4):
        hist.append({"role": "user", "content": f"turn {i}"})
        out = intake.intake_turn(llm, p, c, hist)
        c = c.merge(out["colony_patch"])
        hist.append({"role": "assistant", "content": out["reply"]})
    assert out["complete"] and len(c.members) == 3
