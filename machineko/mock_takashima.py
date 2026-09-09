"""高島市（どうぶつ基金 行政枠）のモック応答。デモ用の固定値。本番経路では使わない。
内容は municipality/takashima/sources/ の市HP本文・基金FAQ・基金規約から人手で起こしたもの。
"""
from __future__ import annotations

import json
from pathlib import Path

SAMPLE = json.loads((Path(__file__).resolve().parent.parent / "demo" / "sample_colony_takashima.json").read_text(encoding="utf-8"))
PAGE, FAQ, REG = "takashima_page.md", "kikin_faq.md", "kikin_register.md"


def _rules():
    return [
        {"id": "R1", "category": "申請者要件", "requirement": "チケットの交付を受けられるのは、市内で活動する団体（市内に活動拠点があるか代表者が市内在住）または市内に住居を有し現に生活する個人。", "applies_when": "常に", "source_file": PAGE, "source_quote": "チケットの交付を受けることができる者は…市内で活動する団体…または市内に住居を有し、現に生活を営む個人です"},
        {"id": "R2", "category": "活動場所", "requirement": "対象は飼い主のいない猫（TNR目的）。飼い猫・飼う予定の猫・保護猫・譲渡予定の猫は対象外。リターンを中止した猫にチケットを使うと無効となり手術費を返金。", "applies_when": "常に", "source_file": FAQ, "source_quote": "チケットはTNRを目的とした飼い主不明猫に使用できます…リターンを中止した場合…チケットは使用できません…手術費用をご返金いただきます"},
        {"id": "R3", "category": "期限", "requirement": "チケットは毎月6日から末日までに環境政策課へ申し込む。交付されるのは翌々月分（例：4月6日申請→6月分）。", "applies_when": "チケットが必要なとき", "source_file": PAGE, "source_quote": "毎月6日から末日までに必要な枚数を環境政策課にお申込みいただくと、「翌々月分」のチケットを後日お渡しします"},
        {"id": "R4", "category": "提出書類", "requirement": "初回は 様式第1号 実施団体届出書、団体の定款又は規約、役員名簿または構成員名簿を提出。個人の場合は団体書類が不要かは要綱で要確認。", "applies_when": "初回申請時", "source_file": PAGE, "source_quote": "初めて申請するボランティア団体等は、次の書類を提出してください。（様式第1号）…団体の定款又は規約…役員名簿または構成員名簿"},
        {"id": "R5", "category": "提出書類", "requirement": "チケット申請は 様式第2号 交付申請書で行う。上限があり申請どおりに交付されないことがある。希望する協力病院で手術できない場合がある。", "applies_when": "チケット申請時", "source_file": PAGE, "source_quote": "（様式第2号）さくらねこ無料不妊手術チケット交付申請書 …無料チケットには上限があるため、申請どおりに交付できない場合があります…希望する協力病院で、不妊手術ができない場合があります"},
        {"id": "R6", "category": "登録後の義務", "requirement": "手術後は 第5号様式 利用報告書と、手術前後の全体像の写真、さくら耳部分の写真（手術前・手術後）を提出。", "applies_when": "手術後", "source_file": PAGE, "source_quote": "（第5号様式）…利用報告書／全体像が分かる写真（手術前・手術後）／さくら耳部分が分かる写真（手術前・手術後）"},
        {"id": "R7", "category": "期限", "requirement": "チケットは有効期限内に使う。期限内に使えなくても延長不可。病院の予約が取れなくても変更・延長不可。配分確定後すぐに予約する。", "applies_when": "チケット交付後", "source_file": FAQ, "source_quote": "予約が取れなかった場合、病院の変更や有効期限の延長はできません…チケット配分が確定次第、ご予約されるようお勧めいたします"},
        {"id": "R8", "category": "期限", "requirement": "報告しないと次のチケットを申請できない。2回未報告でマイページからの申請不可。", "applies_when": "手術後", "source_file": FAQ, "source_quote": "２回のチケット報告がされなかった場合は、チケット申請をご利用頂けません"},
        {"id": "R9", "category": "その他", "requirement": "費用は手術・ワクチン・ノミ駆除が無料。病院までの運搬費と雑費は自己負担。協力病院は基金の一覧から選ぶ。", "applies_when": "常に", "source_file": PAGE, "source_quote": "手術に係る費用（不妊手術費、ワクチン代、ノミ駆除代）が無料です。病院までの運搬費やその他の雑費は自己負担です"},
        {"id": "R10", "category": "その他", "requirement": "TNR実施前後の写真を撮る。", "applies_when": "捕獲時・手術後", "source_file": PAGE, "source_quote": "TNR実施前後の写真が必要です。お忘れなく撮影してください"},
    ]


def _check(colony) -> dict:
    c = colony.to_dict()
    f = []
    members = c.get("members") or []
    resident = any(m.get("is_resident") for m in members)
    n, e = c.get("cat_count"), c.get("ear_tipped_count")
    if members and resident:
        f.append({"level": "OK", "rule_id": "R1", "message": f"申請者 {members[0].get('name')} は市内在住の個人。交付対象です。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R1", "message": "申請者が市内在住か、団体の活動拠点が市内かが未確認です。", "action": "住所を確認してください。"})
    if c.get("kittens_present"):
        f.append({"level": "注意", "rule_id": "R2", "message": "子猫がいます。保護や譲渡に切り替えた猫にはチケットを使えません（使うと無効・返金）。子猫の扱いは本ツールの範囲外です。", "action": "リターンする猫だけを申請枚数に数えてください。"})
    if n is not None and e is not None:
        f.append({"level": "OK", "rule_id": "R5", "message": f"未手術 {n - e} 頭。様式第2号で {n - e} 枚を申請します。上限で減らされることがあります。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R5", "message": "頭数と手術済頭数が未入力です。申請枚数が決まりません。", "action": "現在の頭数と耳カット済の数を確認してください。"})
    f.append({"level": "注意", "rule_id": "R4", "message": "初回申請です。個人の場合、団体の定款・名簿が不要かは交付要綱（PDF未取得）で確認が必要です。", "action": "環境政策課に個人申請時の必要書類を確認してください。"})
    f.append({"level": "注意", "rule_id": "R3", "message": "受付は毎月6日〜末日、交付は翌々月分。準備完了日から最短のチケット有効月は「5. 日程表」で計算します。", "action": "受付期間内に様式第2号を出してください。"})
    if c.get("issues") and "病院" in c["issues"]:
        f.append({"level": "注意", "rule_id": "R7", "message": "協力病院が遠く、1日に運べる頭数が限られます。有効月内に全頭を運べる枚数だけ申請し、配分確定後すぐに予約してください。延長はできません。", "action": "運搬計画を立ててから枚数を決めてください。"})
    f.append({"level": "注意", "rule_id": "R6", "message": "手術前後の写真（全体像・さくら耳）が報告に必要です。捕獲時に撮り忘れると報告できません。", "action": "捕獲時と手術後に写真を撮ってください。"})
    ready = not any(x["level"] == "不足" for x in f)
    return {"findings": f, "ready_to_apply": ready}


def _timeline_spec() -> dict:
    return {
        "steps": [
            {"key": "apply", "label": "実施団体届出書（初回）とチケット交付申請書を提出", "who_decides_date": "申請者", "description": "毎月6日〜末日に環境政策課へ。初回は様式第1号と団体書類も。", "documents": ["様式第1号 実施団体届出書（初回のみ）", "様式第2号 チケット交付申請書"], "source_quote": "毎月6日から末日までに必要な枚数を環境政策課にお申込み"},
            {"key": "review", "label": "市の審査・基金への枚数取りまとめ", "who_decides_date": "自治体", "description": "上限があり申請どおりに交付されないことがある。所要日数は資料に記載なし。", "documents": [], "source_quote": "無料チケットには上限があるため、申請どおりに交付できない場合があります"},
            {"key": "register", "label": "チケット交付（翌々月分）", "who_decides_date": "規則で固定", "description": "申請月の翌々月分のチケットを後日受け取る。有効期間はその1か月。", "documents": [], "source_quote": "「翌々月分」のチケットを後日お渡しします。（例：4月6日に申請 → 6月分のチケット配布）"},
            {"key": "notify", "label": "協力病院の予約", "who_decides_date": "個別調整", "description": "配分確定後すぐに協力病院へ予約。希望病院で受けられない場合がある。地域への周知の定めは資料に記載なし。", "documents": [], "source_quote": "チケット配分が確定次第、ご予約されるようお勧めいたします"},
            {"key": "trap", "label": "捕獲（実施前の写真）", "who_decides_date": "申請者", "description": "捕獲時に全体像とさくら耳部分の写真を撮る。捕獲手順の指導は本ツールの範囲外。", "documents": [], "source_quote": "TNR実施前後の写真が必要です"},
            {"key": "surgery", "label": "協力病院で手術（有効月内）", "who_decides_date": "個別調整", "description": "有効期限内に使う。延長・病院変更は不可。運搬費は自己負担。", "documents": [], "source_quote": "予約が取れなかった場合、病院の変更や有効期限の延長はできません"},
            {"key": "return", "label": "元の場所へ戻す（実施後の写真）", "who_decides_date": "申請者", "description": "リターンを中止するとチケットは無効。", "documents": [], "source_quote": "リターンを中止した場合…チケットは使用できません"},
            {"key": "annual_report", "label": "チケット利用報告書と写真を提出", "who_decides_date": "規則で固定", "description": "手術後、第5号様式と手術前後の写真を提出。報告しないと次の申請ができない。", "documents": ["第5号様式 チケット利用報告書", "手術前後の写真（全体像・さくら耳）"], "source_quote": "報告をしない場合、チケット申請ができなくなります"},
            {"key": "renewal", "label": "次のチケット申請", "who_decides_date": "規則で固定", "description": "猫が残っていれば次の受付期間（毎月6日〜末日）に再申請。", "documents": ["様式第2号 チケット交付申請書"], "source_quote": "さらにチケットが必要な場合は、新たなチケットの申請ができます"},
        ],
        "annual_report_interval_months": None,
        "annual_report_window_days": None,
        "registration_validity_years": None,
        "renewal_window_days_before": None,
        "application_window": {"from_day": 6, "to_day": None, "ticket_month_offset": 2, "valid_months": 1, "max_tickets": None, "report_required_before_next": True,
                               "source_quote": "毎月6日から末日までに…お申込みいただくと、「翌々月分」のチケットを後日お渡しします"},
        "renewal_note": "登録の更新という概念はなく、チケットごとに申請→実施→報告を繰り返す。報告が2回無いと申請不可（基金FAQ）。",
        "termination_note": "廃止届の定めは資料に記載なし。",
        "other_deadlines": [
            {"label": "1年間の報告（アンケート）", "condition": "事業終了後（基金）", "source_quote": "終了後、個別の報告とは別に1年間の報告（アンケート）を提出していただきます"},
        ],
    }


def _wareki(iso: str) -> str:
    if not iso:
        return "令和　年　月　日"
    y, m, d = (int(x) for x in iso.split("-"))
    return f"令和{y - 2018}年{m}月{d}日"


def _fill(ctx, form_key: str) -> dict:
    c = ctx["colony"].to_dict()
    apply_date = ctx.get("apply_date")
    rep = (c.get("members") or [{}])[0]
    w = _wareki(apply_date.isoformat() if apply_date else "")
    cats = c.get("cats") or []
    n_req = max((c.get("cat_count") or 0) - (c.get("ear_tipped_count") or 0), 0)
    if form_key == "registration":
        fields = [
            {"label": "届出日", "value": w, "status": "記入済"},
            {"label": "届出者（団体名または氏名）", "value": rep.get("name", ""), "status": "記入済"},
            {"label": "住所（活動拠点）", "value": rep.get("address", ""), "status": "記入済"},
            {"label": "電話", "value": rep.get("phone", ""), "status": "記入済"},
            {"label": "活動地域", "value": f"高島市{c.get('town','')}（{c.get('location','')}）", "status": "記入済"},
            {"label": "活動内容", "value": f"飼い主のいない猫のTNR。現在{c.get('cat_count')}頭を管理、餌やり{c.get('feeding_time','')}、トイレ{c.get('toilet_count')}か所。", "status": "記入済"},
            {"label": "添付：定款又は規約／役員名簿", "value": "個人のため該当なし（要綱で要確認）", "status": "要確認"},
        ]
        return {"form_title": "様式第1号 飼い主のいない猫不妊手術事業実施団体届出書", "addressed_to": "高島市長 宛", "fields": fields, "cell_edits": [],
                "notes_for_applicant": ["様式の項目名は市HPの記載に基づく暫定です。配布様式（.doc/PDF）を開いて転記してください。", "個人申請の場合の添付書類は交付要綱で確認してください。"]}
    if form_key == "plan":
        fields = [
            {"label": "申請日", "value": w, "status": "記入済"},
            {"label": "申請者", "value": f"{rep.get('name','')}（{rep.get('address','')}／{rep.get('phone','')}）", "status": "記入済"},
            {"label": "希望枚数", "value": f"{n_req}枚（未手術{n_req}頭）", "status": "記入済"},
            {"label": "使用予定月", "value": "申請月の翌々月（5. 日程表で計算）", "status": "要確認"},
            {"label": "希望する協力病院", "value": "", "status": "未入力"},
            {"label": "対象猫の生息場所", "value": f"高島市{c.get('town','')} {c.get('location','')}", "status": "記入済"},
            {"label": "対象猫の内訳", "value": "／".join(f"{x.get('color')}・{x.get('sex')}" for x in cats) or "", "status": "記入済" if cats else "未入力"},
        ]
        return {"form_title": "様式第2号 さくらねこ無料不妊手術チケット交付申請書", "addressed_to": "高島市長 宛", "fields": fields, "cell_edits": [],
                "notes_for_applicant": ["希望する協力病院は基金の協力病院一覧から選んでください。希望病院で受けられない場合があります。", "上限があり申請どおりに交付されないことがあります。"]}
    fields = [
        {"label": "報告日", "value": w, "status": "記入済"},
        {"label": "報告者", "value": rep.get("name", ""), "status": "記入済"},
        {"label": "使用したチケット枚数", "value": f"{n_req}枚", "status": "要確認"},
        {"label": "手術実施日／協力病院", "value": "", "status": "未入力"},
        {"label": "手術した猫（毛色・性別）", "value": "／".join(f"{x.get('color')}・{x.get('sex')}" for x in cats), "status": "記入済" if cats else "未入力"},
        {"label": "添付写真", "value": "全体像（手術前・後）、さくら耳部分（手術前・後）", "status": "要確認"},
    ]
    return {"form_title": "第5号様式 さくらねこ無料不妊手術チケット利用報告書", "addressed_to": "高島市長 宛", "fields": fields, "cell_edits": [],
            "notes_for_applicant": ["写真4種類が無いと報告できません。", "報告しないと次のチケットを申請できません。"]}


def _flyer(ctx) -> str:
    c = ctx["colony"].to_dict()
    rep = (c.get("members") or [{}])[0]
    return f"""近隣の皆さまへ　―　飼い主のいない猫の不妊手術（TNR）のお知らせ

高島市が参加する公益財団法人どうぶつ基金「さくらねこ無料不妊手術事業（行政枠）」により、
{c.get('town','')}（{c.get('location','')}）周辺の飼い主のいない猫に不妊手術を行います。

■ 内容
　猫を一時的に捕獲し、協力病院で不妊手術を受けさせたうえで、元の場所に戻します。
　手術済みの目印として耳先をさくらの花びらの形にカットします（さくら耳）。

■ 捕獲予定期間
　{ctx.get('trap_period') or '令和　年　月（チケット有効月）'}

■ 飼い猫をお飼いの方へ
　誤って捕獲しないため、期間中は首輪を付けるか屋内で過ごさせてください。

■ 連絡先
　{rep.get('name','')}（{rep.get('phone','')}）
　高島市 環境政策課

※ 高島市の資料には地域へのお知らせの参考様式が無いため、京都市の参考様式を参考に作成した文面です。
"""


def _intake(ctx) -> dict:
    turn = len([m for m in ctx["history"] if m["role"] == "user"])
    s = SAMPLE
    if turn <= 1:
        patch = {k: s[k] for k in ("town", "location", "cat_count", "ear_tipped_count", "kittens_present", "cats")}
        return {"reply": f"高島市{s['town']}（{s['location']}）、{s['cat_count']}頭、手術済{s['ear_tipped_count']}頭、子猫あり、で記録します。\n\n餌やりの場所と時間、トイレ、それと病院までの運搬の見込み（車の有無、1日に運べる頭数）を教えてください。", "colony_patch": patch, "complete": False}
    if turn == 2:
        patch = {k: s[k] for k in ("feeding_site", "feeding_sites_count", "feeding_site_is_private", "feeding_site_permission", "feeding_time", "feeding_people", "toilet_site", "toilet_count", "cleaning_time", "cleaning_people", "complaint_contact", "issues")}
        return {"reply": f"餌場は{s['feeding_site']}、{s['feeding_time']}。運搬は「{s['issues']}」で記録します。\n\n最後に申請者です。団体ですか個人ですか。氏名・住所（市内在住か）・電話を教えてください。", "colony_patch": patch, "complete": False}
    patch = {"members": s["members"], "notes": s["notes"]}
    return {"reply": f"{s['members'][0]['name']}（高島市内在住の個人）として記録しました。団体ではないので、様式第1号の団体書類は要綱で要確認です。\n\n聞き取りは以上です。「2. 要綱照合」へ進んでください。", "colony_patch": patch, "complete": True}


def _report(ctx) -> dict:
    rec = ctx["record"]
    turn = len([m for m in ctx["history"] if m["role"] == "user"])
    n = rec.get("cat_count") or 0
    t = rec.get("tickets") or 0
    if turn <= 1:
        return {"reply": f"利用報告を受け付けます。チケット{t}枚のうち何枚を使い、何頭を手術しましたか。手術日と協力病院、写真（全体像・さくら耳、手術前後）の有無も教えてください。", "report": None, "complete": False}
    rep = {"cat_count": n, "ear_tipped_count": (rec.get("ear_tipped_count") or 0) + t, "surgeries": t, "summary": f"チケット{t}枚を全て使用し{t}頭を手術。手術前後の写真（全体像・さくら耳）あり。全頭リターン済。"}
    return {"reply": f"第5号様式の内容が揃いました。使用{t}枚、手術{t}頭、写真あり。「提出」で市の台帳に反映されます。次のチケットは次の受付期間（毎月6日〜末日）に申請できます。", "report": rep, "complete": True}


def dispatch(task: str, ctx: dict):
    if task == "extract_rules":
        return {"rules": _rules()}
    if task == "check_colony":
        return _check(ctx["colony"])
    if task == "timeline_spec":
        return _timeline_spec()
    if task.startswith("fill_"):
        return _fill(ctx, task[len("fill_"):])
    if task == "flyer":
        return _flyer(ctx)
    if task == "intake":
        return _intake(ctx)
    if task == "report":
        return _report(ctx)
    raise KeyError(f"mock_takashima: unknown task {task}")
