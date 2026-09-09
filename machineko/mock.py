"""モック応答。

APIキーが無い環境でも UI が最後まで動くようにするための代替。
ここに書かれた京都市の規則は「デモ用の固定値」であり、本番経路（LLM が一次資料から抽出）では使わない。
内容は municipality/kyoto/sources/ の要綱（yoko060401.pdf）・様式・記載例から人手で起こしたもの。
"""
from __future__ import annotations

import json
from pathlib import Path

SAMPLE = json.loads((Path(__file__).resolve().parent.parent / "demo" / "sample_colony.json").read_text(encoding="utf-8"))
YOKO = "yoko060401.pdf"


def _rules():
    return [
        {"id": "R1", "category": "地域合意", "requirement": "町内会等の合意を得る取組が継続して行われ、かつ代表者の同意が得られていること。", "applies_when": "常に", "source_file": YOKO, "source_quote": "第２条⑴ 町内会等…の合意を得るための取組が継続して行われており、かつ、代表者の同意が得られていること"},
        {"id": "R2", "category": "申請者要件", "requirement": "同一世帯員ではない地域住民2人以上で団体を構成する。", "applies_when": "常に", "source_file": YOKO, "source_quote": "第２条⑵ 同一世帯員ではない地域住民２人以上…による団体を構成して行うものであること"},
        {"id": "R3", "category": "申請者要件", "requirement": "管理する野良猫が10頭以上の場合、同一世帯員ではない地域住民2人を含む京都市民3人以上で構成する。", "applies_when": "頭数が10頭以上", "source_file": YOKO, "source_quote": "第２条⑵ …１０頭以上の場合にあっては同一世帯員ではない地域住民２人を含む京都市民３人以上"},
        {"id": "R4", "category": "活動場所", "requirement": "活動地域は町内会等単位を原則とし、活動地域の野良猫の状況を把握していること。", "applies_when": "常に", "source_file": YOKO, "source_quote": "第２条⑶ 活動地域…にいる野良猫の状況を把握していること。ア 活動地域は、町内会等単位を原則とする"},
        {"id": "R5", "category": "提出書類", "requirement": "登録申請書（第1号様式）に実施計画書（第6号様式）と、活動地域の範囲・給餌の場所・トイレの場所を示した周辺地図を添えて医療衛生センター長に提出する。", "applies_when": "申請時", "source_file": YOKO, "source_quote": "第５条 「まちねこ活動登録申請書」（第１号様式…）に、「まちねこ活動実施計画書」（第６号様式…）及び次に掲げる事項を示した周辺地図を添えて"},
        {"id": "R6", "category": "地域合意", "requirement": "登録申請書に、町内会等の代表者の住所・氏名・電話、説明実施日と実施者、代表者同意のチェックを記入する。代表者の署名・押印は不要。", "applies_when": "申請時", "source_file": "rei_touroku.pdf", "source_quote": "活動について、あらかじめ町内会等の代表者へ説明し、同意を得たことを記載してください。（R6.4.1～）代表者の署名・押印不要"},
        {"id": "R7", "category": "管理方法", "requirement": "実施計画書に、周知方法（町内会への説明・回覧板・掲示板・投函・その他）と実施日・頻度、餌やりの場所数・時間・人数、トイレ設置数、ふん清掃の時間・人数、苦情等の連絡先を記入する。", "applies_when": "申請時", "source_file": "jissikeikaku.docx", "source_quote": "活動内容の地域への周知 方法 町内会への説明・回覧板・掲示板・投函 … 餌やりを行う場所 か所 … トイレの設置数 か所 … 苦情等の連絡先"},
        {"id": "R8", "category": "管理方法", "requirement": "給餌はエサを放置せず適切に管理し、トイレを設置して清掃する。管理する猫は全て避妊去勢手術を実施する。", "applies_when": "登録後", "source_file": "touroku.docx", "source_quote": "裏面（２）「まちねこ」への給餌については、エサの放置等をすることなく…（３）トイレを設置し、清掃を適切に実施…（４）全て避妊去勢手術を実施すること"},
        {"id": "R9", "category": "登録後の義務", "requirement": "手術を依頼するときは避妊去勢手術実施申請書（第4号様式）を提出する。手術日時は動物愛護センターが医療衛生センター長を通じて通知する。", "applies_when": "登録後、捕獲前", "source_file": YOKO, "source_quote": "第９条 …まちねこ避妊去勢手術実施申請書（第４号様式）を医療衛生センター長に提出 ／ 第１０条 手術の実施の日時は、動物愛護センターが…通知する"},
        {"id": "R10", "category": "期限", "requirement": "登録の有効期間は登録の日から3年。", "applies_when": "登録後", "source_file": YOKO, "source_quote": "第５条３ 登録の有効期間は、登録の日から３年間とする"},
        {"id": "R11", "category": "期限", "requirement": "1年ごとに活動状況報告書（第5号様式）を提出する。登録日と同月日から30日以内。更新を行う年度は更新申請書で代えられる。", "applies_when": "登録の翌年以降毎年", "source_file": YOKO, "source_quote": "第１２条 １年ごとに…「まちねこ活動状況報告書」（第５号様式）を提出 ／ ２ 登録した日と同月日…から３０日以内に行う"},
        {"id": "R12", "category": "期限", "requirement": "更新する場合は更新申請書（第2号様式）と実施計画書を、満了日の30日前から満了日までに提出する。", "applies_when": "登録から3年", "source_file": YOKO, "source_quote": "第６条２ …従前の登録の有効期間の満了の日…の３０日前から満了日までに医療衛生センター長に提出"},
        {"id": "R13", "category": "期限", "requirement": "活動を廃止するときは廃止届出書（第3号様式）を提出する。期限までに更新しない場合は職権で登録抹消されることがある。", "applies_when": "活動終了時", "source_file": YOKO, "source_quote": "第７条 …「まちねこ活動廃止届出書」（第３号様式）を…提出しなければならない ／ ３ 期限までに第６条の更新が行われなかったもの…職権で登録を抹消することができる"},
    ]


def _check(colony) -> dict:
    c = colony.to_dict()
    f = []
    members = c.get("members") or []
    residents = [m for m in members if m.get("is_resident")]
    citizens = [m for m in members if m.get("is_kyoto_citizen")]
    n = c.get("cat_count")

    if c.get("consent_obtained") and c.get("explained_date") and c.get("association_rep_name"):
        f.append({"level": "OK", "rule_id": "R1", "message": f"{c.get('neighborhood_association')}代表者 {c['association_rep_name']} に {c['explained_date']} 説明済、同意あり。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R1", "message": "町内会等の代表者の同意、説明実施日、代表者の氏名のいずれかが未入力です。第1号様式の必須欄です。", "action": "代表者の住所・氏名・電話と説明実施日を確認してください。"})
    if len(residents) >= 2:
        f.append({"level": "OK", "rule_id": "R2", "message": f"地域住民が{len(residents)}名います。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R2", "message": f"地域住民が{len(residents)}名です。同一世帯員でない地域住民2名以上が必要です。", "action": "活動地域の住民をもう1名以上加えてください。"})
    if n is None:
        f.append({"level": "不足", "rule_id": "R4", "message": "頭数が未入力です。", "action": "現在管理する猫の頭数と手術済頭数を確認してください。"})
    elif n >= 10:
        if len(residents) >= 2 and len(citizens) >= 3:
            f.append({"level": "OK", "rule_id": "R3", "message": f"{n}頭（10頭以上）のため京都市民3名以上が必要ですが、京都市民{len(citizens)}名（うち地域住民{len(residents)}名）で満たしています。", "action": ""})
        else:
            f.append({"level": "不足", "rule_id": "R3", "message": f"{n}頭（10頭以上）のため、地域住民2名を含む京都市民3名以上が必要です。現在は京都市民{len(citizens)}名、地域住民{len(residents)}名。", "action": "京都市民の活動者を追加してください（同一町内でなくても可）。"})
    else:
        f.append({"level": "OK", "rule_id": "R3", "message": f"{n}頭（10頭未満）のため、3名要件は適用されません。", "action": ""})
    if c.get("town"):
        f.append({"level": "OK", "rule_id": "R4", "message": f"活動地域は {c.get('ward')}{c['town']}（町内会等単位）。頭数 {n}、手術済 {c.get('ear_tipped_count')}。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R4", "message": "活動地域の町内が未入力です。活動地域は町内会等単位が原則です。", "action": "町内名を確認してください。"})
    f.append({"level": "注意", "rule_id": "R5", "message": "第1号様式・第6号様式は本ツールで出力しますが、周辺地図（活動地域の範囲・餌場・トイレの位置）は別途添付が必要です。", "action": "地図を用意し、餌場とトイレの位置を書き込んでください。"})
    missing7 = [k for k in ("notify_methods", "feeding_sites_count", "feeding_time", "feeding_people", "toilet_count", "cleaning_time", "cleaning_people", "complaint_contact") if not c.get(k)]
    if not missing7:
        f.append({"level": "OK", "rule_id": "R7", "message": f"周知方法（{'・'.join(c['notify_methods'])}）、餌やり{c['feeding_sites_count']}か所・{c['feeding_people']}人、トイレ{c['toilet_count']}か所、清掃{c['cleaning_people']}人、苦情連絡先が揃っています。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R7", "message": f"第6号様式の欄が未入力です：{', '.join(missing7)}", "action": "餌やり・トイレ・清掃・周知の各項目を確認してください。"})
    if c.get("feeding_site_is_private") is False:
        f.append({"level": "注意", "rule_id": "R8", "message": "餌場が私有地ではありません。エサを放置しない管理と、場所の管理者の了解を確認してください。", "action": "餌場の土地の管理者に承諾を得てください。"})
    if n is not None and c.get("ear_tipped_count") is not None:
        f.append({"level": "注意", "rule_id": "R9", "message": f"未手術 {n - c['ear_tipped_count']} 頭。登録後、捕獲前に第4号様式（手術実施申請書）の提出が必要です。手術日はセンターから通知されます。", "action": "登録通知が届いたら第4号様式を提出してください。"})
    if c.get("kittens_present"):
        f.append({"level": "注意", "rule_id": "R8", "message": "子猫がいると回答されています。子猫の扱いは本ツールの範囲外です。", "action": "手術可能な月齢についてはセンターに確認してください。"})
    ready = not any(x["level"] == "不足" for x in f)
    return {"findings": f, "ready_to_apply": ready}


def _timeline_spec() -> dict:
    return {
        "steps": [
            {"key": "apply", "label": "登録申請書・実施計画書・周辺地図を提出", "who_decides_date": "申請者", "description": "第1号様式と第6号様式に周辺地図を添えて医療衛生センター長へ提出。", "documents": ["第１号様式 まちねこ活動登録申請書", "第６号様式 まちねこ活動実施計画書", "周辺地図（活動地域の範囲・給餌場所・トイレ）"], "source_quote": "第５条 …周辺地図を添えて、医療衛生センター長に提出するものとする"},
            {"key": "review", "label": "書類審査・現地調査", "who_decides_date": "自治体", "description": "代表者同意と周知方法の確認、現地調査。所要日数は資料に記載なし。", "documents": [], "source_quote": "第５条２ ⑴ 町内会等を代表する者の同意及び地域への周知方法の確認 ⑵ 現地調査等による…確認"},
            {"key": "register", "label": "登録（有効3年）・通知", "who_decides_date": "自治体", "description": "登録の日から3年間有効。団体に通知され、動物愛護センターに写しが送付される。", "documents": [], "source_quote": "第５条３ 登録の有効期間は、登録の日から３年間とする"},
            {"key": "notify", "label": "町内会等で活動の周知", "who_decides_date": "申請者", "description": "参考様式のお知らせチラシで周知。実施計画書に書いた方法（説明・回覧板・掲示板・投函）で行う。", "documents": ["参考様式 まちねこ活動のお知らせ"], "source_quote": "※まちねこ活動者：必要に応じて、参考様式のお知らせチラシで周知"},
            {"key": "trap", "label": "手術実施申請・保護器貸出・捕獲", "who_decides_date": "個別調整", "description": "第4号様式を提出。保護器は各区医療衛生コーナー又は動物愛護センターで貸出。捕獲手順の指導は本ツールの範囲外。", "documents": ["第４号様式 まちねこ避妊去勢手術実施申請書"], "source_quote": "第８条４ 猫保護器の貸出しは、各区医療衛生コーナー…又は動物愛護センターにおいて行う ／ 第９条 …第４号様式"},
            {"key": "surgery", "label": "指定日時に持込・避妊去勢手術", "who_decides_date": "自治体", "description": "手術日時は動物愛護センターが医療衛生センター長を通じて通知。指定日時に各区医療衛生コーナー又は動物愛護センターへ搬入。手術前12時間は絶食。", "documents": [], "source_quote": "第１０条 避妊去勢手術の実施の日時は、動物愛護センターが医療衛生センター長を通じ、まちねこ活動団体に通知する"},
            {"key": "return", "label": "放猫（元の場所へ戻す）", "who_decides_date": "個別調整", "description": "動物愛護センター職員が放猫。日時は医療衛生センターが調整。活動団体が立ち会う。", "documents": [], "source_quote": "第１１条 避妊去勢手術したまちねこは、動物愛護センター職員により放猫を行う。２ …医療衛生センターは、日時等の調整を行う"},
            {"key": "annual_report", "label": "活動状況報告書の提出", "who_decides_date": "規則で固定", "description": "登録日と同月日から30日以内に第5号様式を提出。更新を行う年度は更新申請書で代えられる。", "documents": ["第５号様式 まちねこ活動状況報告書"], "source_quote": "第１２条２ …登録した日と同月日…から３０日以内に行うものとする"},
            {"key": "renewal", "label": "登録更新申請", "who_decides_date": "規則で固定", "description": "満了日の30日前から満了日までに第2号様式と実施計画書を提出。更新後の有効期間は満了日の翌日から3年。", "documents": ["第２号様式 まちねこ活動登録更新申請書", "第６号様式 まちねこ活動実施計画書"], "source_quote": "第６条２ …満了日の３０日前から満了日までに医療衛生センター長に提出するものとする"},
        ],
        "annual_report_interval_months": 12,
        "annual_report_window_days": 30,
        "registration_validity_years": 3,
        "renewal_window_days_before": 30,
        "renewal_note": "満了日の30日前から満了日までに第2号様式と実施計画書を提出（第6条2項）。期限までに更新しないと職権で抹消されることがある（第7条3項）。",
        "termination_note": "活動を廃止するときは第3号様式（廃止届出書）を提出（第7条1項）。",
        "other_deadlines": [
            {"label": "第３号様式 まちねこ活動廃止届出書", "condition": "活動を廃止しようとするとき", "source_quote": "第７条 …「まちねこ活動廃止届出書」（第３号様式）を医療衛生センター長に提出しなければならない"},
            {"label": "第４号様式 避妊去勢手術実施申請書", "condition": "手術を依頼するとき（捕獲の前）", "source_quote": "第９条 …まちねこ避妊去勢手術実施申請書（第４号様式）を医療衛生センター長に提出する"},
        ],
    }


def _wareki(iso: str) -> str:
    if not iso:
        return ""
    try:
        y, m, d = (int(x) for x in iso.split("-"))
    except ValueError:
        return iso
    return f"令和{y - 2018}年{m}月{d}日"


def _wareki_parts(iso: str) -> tuple[str, str, str]:
    if not iso:
        return ("", "", "")
    y, m, d = (int(x) for x in iso.split("-"))
    return (f"令和{y - 2018}", str(m), str(d))


def _fill(ctx, form_key: str) -> dict:
    c = ctx["colony"].to_dict()
    apply_date = ctx.get("apply_date")
    members = c.get("members") or []
    rep = next((m for m in members if "代表" in (m.get("role") or "")), members[0] if members else {})
    apply_iso = apply_date.isoformat() if apply_date else ""
    apply_w = _wareki(apply_iso) if apply_iso else "令和　年　月　日"
    cells = ctx.get("cells") or []
    has_template = bool(cells)

    if form_key == "registration":
        ay, am, ad = _wareki_parts(apply_iso)
        ey, em, ed = _wareki_parts(c.get("explained_date", ""))
        fields = [
            {"label": "申請日", "value": apply_w, "status": "記入済" if apply_date else "未入力"},
        ]
        for i, m in enumerate(members[:3], 1):
            fields.append({"label": f"活動者{i} 住所／氏名／電話", "value": f"{m.get('address','')}／{m.get('name','')}／{m.get('phone','')}" + ("（主たる連絡先）" if m is rep else ""), "status": "記入済"})
        fields += [
            {"label": "活動する地域", "value": f"{c.get('ward','')}　{c.get('town','')}", "status": "記入済" if c.get("town") else "未入力"},
            {"label": "申請者を含む活動者数", "value": f"{len(members)}名", "status": "記入済"},
            {"label": "管理する猫の頭数", "value": f"{c.get('cat_count')}頭", "status": "記入済"},
            {"label": "町内会等の代表者 住所", "value": c.get("association_rep_address", ""), "status": "記入済" if c.get("association_rep_address") else "未入力"},
            {"label": "町内会等の代表者 氏名／電話", "value": f"{c.get('association_rep_name','')}／{c.get('association_rep_phone','')}", "status": "記入済" if c.get("association_rep_name") else "未入力"},
            {"label": "説明実施日／実施者", "value": f"{_wareki(c.get('explained_date',''))}／{c.get('explained_by','')}", "status": "記入済" if c.get("explained_date") else "未入力"},
            {"label": "町内会等の代表者同意", "value": "☑ 同意あり" if c.get("consent_obtained") else "□", "status": "記入済" if c.get("consent_obtained") else "未入力"},
            {"label": "添付書類", "value": "１ 実施計画書（第6号様式）　２ 周辺地図　３ エサ場・トイレの設置場所を示したもの", "status": "要確認"},
        ]
        edits = []
        if has_template:
            edits.append({"table": 0, "row": 0, "col": 1, "text": f"{ay}年　{am}月　{ad}日"})
            for i, m in enumerate(members[:3]):
                edits.append({"table": 0, "row": 1 + i, "col": 0, "text": f"住所\n{m.get('address','')}"})
                edits.append({"table": 0, "row": 1 + i, "col": 1, "text": f"活動者氏名\n{m.get('name','')}\n電話　{m.get('phone','')}"})
                edits.append({"table": 0, "row": 1 + i, "col": 2, "text": "☑" if m is rep else "□"})
            edits.append({"table": 1, "row": 1, "col": 1, "text": f"{c.get('ward','')}区　　　{c.get('town','')}　町内".replace("区区", "区")})
            edits.append({"table": 1, "row": 2, "col": 1, "text": f"{len(members)}　名"})
            edits.append({"table": 1, "row": 3, "col": 1, "text": f"{c.get('cat_count')}　頭"})
            edits.append({"table": 1, "row": 4, "col": 1, "text": f"住所　{c.get('association_rep_address','')}"})
            edits.append({"table": 1, "row": 5, "col": 1, "text": f"氏名　{c.get('association_rep_name','')}　　電話　{c.get('association_rep_phone','')}"})
            edits.append({"table": 1, "row": 6, "col": 1, "text": f"説明実施日　{ey}年　{em}月　{ed}日　　実施者：{c.get('explained_by','')}"})
            edits.append({"table": 1, "row": 7, "col": 1, "text": ("☑" if c.get("consent_obtained") else "□") + "　町内会等の代表者同意（※同意ありの場合、□にチェックしてください）"})
        notes = ["周辺地図（町内会等が分かるもの）と、エサ場・トイレの設置場所を示した図は別途添付してください。",
                 "裏面の記載事項（給餌管理、トイレ清掃、全頭手術、保護器の扱い等）に活動者全員が同意している必要があります。"]
        return {"form_title": "第１号様式 まちねこ活動登録申請書", "addressed_to": "（宛先）京都市医療衛生センター長", "fields": fields, "cell_edits": edits, "notes_for_applicant": notes}

    # 第6号様式
    ey, em, ed = _wareki_parts(c.get("explained_date", ""))
    methods_all = ["町内会への説明", "回覧板", "掲示板", "投函"]
    chosen = c.get("notify_methods") or []
    others = [m for m in chosen if m not in methods_all]
    fields = [
        {"label": "活動代表者氏名／電話", "value": f"{rep.get('name','')}／{rep.get('phone','')}", "status": "記入済"},
        {"label": "現在の活動人数", "value": f"{len(members)}人", "status": "記入済"},
        {"label": "現在管理する猫", "value": f"{c.get('cat_count')}頭", "status": "記入済"},
        {"label": "うち、避妊去勢手術実施済", "value": f"{c.get('ear_tipped_count')}頭", "status": "記入済"},
        {"label": "地域への周知 方法", "value": "・".join(chosen) if chosen else "", "status": "記入済" if chosen else "未入力"},
        {"label": "地域への周知 実施日／頻度", "value": f"{_wareki(c.get('explained_date',''))}／年{c.get('notify_frequency_per_year') or '　'}回", "status": "記入済" if c.get("explained_date") else "未入力"},
        {"label": "餌やりを行う場所", "value": f"{c.get('feeding_sites_count')}か所（{c.get('feeding_site','')}）", "status": "記入済" if c.get("feeding_sites_count") else "未入力"},
        {"label": "餌やりを行う時間・人数", "value": f"{c.get('feeding_time','')}　{c.get('feeding_people')}人", "status": "記入済" if c.get("feeding_time") else "未入力"},
        {"label": "トイレの設置数", "value": f"{c.get('toilet_count')}か所（{c.get('toilet_site','')}）", "status": "記入済" if c.get("toilet_count") else "未入力"},
        {"label": "ふんの清掃を行う時間・人数", "value": f"{c.get('cleaning_time','')}　{c.get('cleaning_people')}人", "status": "記入済" if c.get("cleaning_time") else "未入力"},
        {"label": "苦情等の連絡先", "value": c.get("complaint_contact", ""), "status": "記入済" if c.get("complaint_contact") else "未入力"},
        {"label": "苦情対応事例", "value": c.get("complaint_cases") or "特になし", "status": "要確認"},
        {"label": "活動における問題点などその他参考事項", "value": c.get("issues") or "特になし", "status": "記入済"},
        {"label": "まちねこ活動の効果", "value": "（更新・終了時に記入）", "status": "記入済"},
    ]
    edits = []
    if has_template:
        edits.append({"table": 0, "row": 0, "col": 0, "text": f"活動代表者氏名　{rep.get('name','')}"})
        edits.append({"table": 0, "row": 0, "col": 1, "text": f"電話　{rep.get('phone','')}"})
        edits.append({"table": 0, "row": 1, "col": 1, "text": f"{len(members)}　人"})
        edits.append({"table": 0, "row": 2, "col": 1, "text": f"現在管理する猫\n{c.get('cat_count')}　頭"})
        edits.append({"table": 0, "row": 2, "col": 3, "text": f"うち、避妊去勢手術実施済\n{c.get('ear_tipped_count')}　頭"})
        marks = "　・".join(("☑" if m in chosen else "") + m for m in methods_all)
        edits.append({"table": 0, "row": 3, "col": 2, "text": f"{marks}\nその他（{'・'.join(others)}）"})
        edits.append({"table": 0, "row": 4, "col": 2, "text": f"{ey}年 {em}月 {ed}日"})
        edits.append({"table": 0, "row": 4, "col": 4, "text": f"年　{c.get('notify_frequency_per_year') or '　'}　回"})
        edits.append({"table": 0, "row": 5, "col": 1, "text": f"{c.get('feeding_sites_count')}　か所"})
        edits.append({"table": 0, "row": 6, "col": 1, "text": f"{c.get('feeding_time','')}　{c.get('feeding_people')}人"})
        edits.append({"table": 0, "row": 7, "col": 1, "text": f"{c.get('toilet_count')}　か所"})
        edits.append({"table": 0, "row": 8, "col": 1, "text": f"{c.get('cleaning_time','')}　{c.get('cleaning_people')}人"})
        edits.append({"table": 0, "row": 9, "col": 1, "text": c.get("complaint_contact", "")})
        edits.append({"table": 0, "row": 10, "col": 1, "text": c.get("complaint_cases") or "特になし"})
        edits.append({"table": 0, "row": 11, "col": 1, "text": c.get("issues") or "特になし"})
    notes = ["周知の実施日は町内会等への説明実施日を入れています。回覧・掲示を別日に行う場合は書き換えてください。",
             "苦情対応事例は記載例に倣い「特になし」としています。事例があれば追記してください。"]
    return {"form_title": "第６号様式 まちねこ活動実施計画書", "addressed_to": "", "fields": fields, "cell_edits": edits, "notes_for_applicant": notes}


def _flyer(ctx) -> str:
    c = ctx["colony"].to_dict()
    p = ctx["profile"]
    rep = next((m for m in c.get("members") or [] if "代表" in (m.get("role") or "")), (c.get("members") or [{}])[0])
    period = ctx.get("trap_period") or "令和　年　月　日 〜 令和　年　月　日"
    return f"""近隣の皆さまへ
～まちねこ活動のお知らせ～

京都市の「まちねこ活動」地域に登録し、野良猫を増やさない取組みを行います。

◎ まちねこ活動とは・・・
　地域にいる所有者不明猫を、活動者が保護し、避妊去勢手術の後、元にいた場所へ戻し、適切に餌を与え、食べ残しやふんの清掃をする活動です。
　地域の理解を得ながら、しっかりとルールを決めて活動することで、以下の効果が期待できます。

〇 野良猫の繁殖を防止し、鳴き声の軽減や、野良猫の数を減らす効果
〇 トイレの設置、清掃の実施による、ふん尿被害の軽減
〇 適切な餌やりによる、清潔の保持

◎ 活動内容
・餌や水を与えるルールを決める。　・避妊去勢手術を実施する。
・トイレの設置や周辺の清掃を行う　など

◎ 登録により京都市から受ける支援
・避妊去勢手術の無償実施　・保護器の貸出し
・活動にあたっての助言　など

ご理解とご協力をよろしくお願いします。

活動予定地域：{c.get('ward','')}{c.get('town','')}　町内
活動代表者：{rep.get('name','')}（{rep.get('phone','')}）

―― 補足（参考様式への追記） ――
・保護器（捕獲かご）の設置予定期間：{period}
・期間中、飼い猫は首輪を付けるか屋内で過ごさせてください。誤って保護した場合は上記代表者までご連絡ください。
・餌やりは活動者が決めた場所・時間で行い、片付けまで行います。
・京都市{p.office}：{'／'.join(p.contacts)}
"""


def _intake(ctx) -> dict:
    """台本どおりに進む聞き取り。ユーザーの発言内容は読まず、サンプルコロニーを段階的に埋める。"""
    turn = len([m for m in ctx["history"] if m["role"] == "user"])
    s = SAMPLE
    if turn <= 1:
        patch = {k: s[k] for k in ("ward", "town", "location", "cat_count", "ear_tipped_count", "kittens_present")}
        reply = (f"承知しました。活動地域は{s['ward']}{s['town']}（{s['location']}）、現在{s['cat_count']}頭、うち手術済{s['ear_tipped_count']}頭、子猫なし、で記録します。\n\n"
                 "次に管理方法を伺います。餌やりの場所は何か所で、どこですか（私有地なら誰の敷地・承諾か）。餌やりの時間帯と人数、食べ残しの片付け方も教えてください。")
        return {"reply": reply, "colony_patch": patch, "complete": False}
    if turn == 2:
        patch = {k: s[k] for k in ("feeding_site", "feeding_sites_count", "feeding_site_is_private", "feeding_site_permission", "feeding_time", "feeding_people")}
        reply = (f"餌やりは{s['feeding_sites_count']}か所（{s['feeding_site']}、{s['feeding_site_permission']}）、{s['feeding_time']}、{s['feeding_people']}人で記録します。\n\n"
                 "トイレの設置数と場所、ふんの清掃を行う時間と人数、苦情があったときの連絡先を教えてください。")
        return {"reply": reply, "colony_patch": patch, "complete": False}
    if turn == 3:
        patch = {k: s[k] for k in ("toilet_site", "toilet_count", "cleaning_time", "cleaning_people", "complaint_contact", "issues")}
        reply = (f"トイレは{s['toilet_site']}に{s['toilet_count']}か所、清掃は{s['cleaning_time']}に{s['cleaning_people']}人、苦情連絡先は{s['complaint_contact']}、で記録します。\n\n"
                 "次に地域の合意です。町内会等の名称と代表者（住所・氏名・電話）、説明を行った日と実施者、代表者の同意を得られたか、周知の方法（町内会への説明・回覧板・掲示板・投函）を教えてください。")
        return {"reply": reply, "colony_patch": patch, "complete": False}
    if turn == 4:
        patch = {k: s[k] for k in ("neighborhood_association", "association_rep_name", "association_rep_address", "association_rep_phone", "explained_date", "explained_by", "consent_obtained", "notify_methods", "notify_frequency_per_year")}
        reply = (f"{s['neighborhood_association']}の代表者 {s['association_rep_name']} に {s['explained_date']} に {s['explained_by']} が説明し、同意あり。周知は{'・'.join(s['notify_methods'])}、年{s['notify_frequency_per_year']}回、で記録します。\n\n"
                 "最後に活動者です。一緒に活動する方の氏名・住所・電話番号と、その方が活動地域の住民か、京都市民かを全員分教えてください。"
                 f"頭数が{s['cat_count']}頭（10頭以上）なので、同一世帯でない地域住民2名を含む京都市民3名以上が必要です。")
        return {"reply": reply, "colony_patch": patch, "complete": False}
    patch = {"members": s["members"], "notes": s["notes"]}
    names = "、".join(m["name"] for m in s["members"])
    reply = (f"活動者3名（{names}）を記録しました。地域住民2名・京都市民3名で、10頭以上の要件を満たします。主たる連絡先は{s['members'][0]['name']}とします。\n\n"
             "聞き取りは以上です。左のメニューから「2. 要綱照合」に進んでください。")
    return {"reply": reply, "colony_patch": patch, "complete": True}


def _report(ctx) -> dict:
    """年次報告の台本。2ターンで完了する。"""
    rec = ctx["record"]
    turn = len([m for m in ctx["history"] if m["role"] == "user"])
    n0, e0 = rec.get("cat_count") or 0, rec.get("ear_tipped_count") or 0
    n1 = n0 + 1
    if turn <= 1:
        return {"reply": f"現在{n1}頭、全頭手術済みで記録しました。この1年で手術した頭数と、その他の報告事項（効果、苦情対応の状況、課題、活動内容の変更など）を教えてください。", "report": None, "complete": False}
    rep = {"cat_count": n1, "ear_tipped_count": n1, "surgeries": n1 - e0,
           "summary": f"登録時{n0}頭から{n1}頭（新規流入1頭）。未手術{n0 - e0}頭と新規1頭の計{n1 - e0}頭を手術し、全頭手術済。子猫の出生なし。苦情なし。活動内容の変更なし。"}
    return {"reply": f"以上で第５号様式（活動状況報告書）の内容が揃いました。\n\n現在管理する猫 {n1}頭、うち手術済 {n1}頭。この1年の手術 {n1 - e0}頭、新規流入1頭、苦情なし。\n\n「提出」を押すと医療衛生センターの台帳に反映されます。", "report": rep, "complete": True}


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
    raise KeyError(f"mock: unknown task {task}")
