"""モック応答。

APIキーが無い環境でも UI が最後まで動くようにするための代替。
ここに書かれた京都市の規則は「デモ用の固定値」であり、本番経路（LLM が一次資料から抽出）では使わない。
出典：municipality/kyoto/sources/notes.md（京都市HP https://www.city.kyoto.lg.jp/hokenfukushi/page/0000189400.html）
"""
from __future__ import annotations

import json
from pathlib import Path

SAMPLE = json.loads((Path(__file__).resolve().parent.parent / "demo" / "sample_colony.json").read_text(encoding="utf-8"))


def _rules():
    src = "notes.md"
    return [
        {"id": "R1", "category": "申請者要件", "requirement": "活動グループは地域住民2名以上で構成する。", "applies_when": "常に", "source_file": src, "source_quote": "活動グループをつくる：地域住民2名以上"},
        {"id": "R2", "category": "申請者要件", "requirement": "猫が10頭以上の場合、地域住民2名を含む京都市民3名以上で構成する。", "applies_when": "頭数が10頭以上", "source_file": src, "source_quote": "猫が10頭以上の場合は、地域住民2名を含む京都市民3名以上"},
        {"id": "R3", "category": "地域合意", "requirement": "町内会等へ説明し、申請書に説明した日付と同意チェックを記入する（町内会長の署名は不要）。", "applies_when": "常に", "source_file": src, "source_quote": "申請書に「町内会等へ説明した日付」と「同意を得たことのチェック欄」を記入する"},
        {"id": "R4", "category": "管理方法", "requirement": "餌場・トイレの場所を定め、餌やりの時間と片付け方法を決める。餌場は正当な権原のある私有地内など。", "applies_when": "常に", "source_file": src, "source_quote": "餌場・トイレの場所（正当な権原のある私有地内など）、餌やりの時間・片付け"},
        {"id": "R5", "category": "管理方法", "requirement": "生息状況（頭数、耳カット済みの有無）を把握する。", "applies_when": "常に", "source_file": src, "source_quote": "生息状況の把握（頭数、耳カット済みの有無）"},
        {"id": "R6", "category": "提出書類", "requirement": "第1号様式（登録申請書）と第6号様式（活動実施計画書）を医療衛生センターへ提出する。", "applies_when": "申請時", "source_file": src, "source_quote": "「まちねこ活動登録申請書（第1号様式）」と「まちねこ活動実施計画書（第6号様式）」を提出"},
        {"id": "R7", "category": "登録後の義務", "requirement": "捕獲の前に地域住民へ周知する。", "applies_when": "登録後", "source_file": src, "source_quote": "地域住民へ周知（参考様式「地域へのお知らせ」）したうえで捕獲"},
        {"id": "R8", "category": "登録後の義務", "requirement": "1年ごとに活動状況（頭数の推移など）を報告する。", "applies_when": "登録後", "source_file": src, "source_quote": "1年ごとに活動状況（頭数の推移など）を報告する"},
        {"id": "R9", "category": "期限", "requirement": "登録の有効期間は登録日から3年。継続する場合は更新申請。", "applies_when": "登録から3年", "source_file": src, "source_quote": "登録の有効期間は登録日から3年間"},
        {"id": "R10", "category": "期限", "requirement": "活動をやめるときは活動廃止届を提出する。", "applies_when": "活動終了時", "source_file": src, "source_quote": "活動をやめるときは活動廃止届"},
    ]


def _check(colony) -> dict:
    c = colony.to_dict()
    f = []
    members = c.get("members") or []
    residents = [m for m in members if m.get("is_resident")]
    citizens = [m for m in members if m.get("is_kyoto_citizen")]
    n = c.get("cat_count")

    if len(residents) >= 2:
        f.append({"level": "OK", "rule_id": "R1", "message": f"地域住民が{len(residents)}名います。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R1", "message": f"地域住民が{len(residents)}名です。2名以上が必要です。", "action": "活動場所の地域住民をもう1名以上加えてください。"})
    if n is None:
        f.append({"level": "不足", "rule_id": "R5", "message": "頭数が未入力です。", "action": "現在の頭数と耳カット済み頭数を確認してください。"})
    elif n >= 10:
        if len(residents) >= 2 and len(citizens) >= 3:
            f.append({"level": "OK", "rule_id": "R2", "message": f"{n}頭のため京都市民3名以上が必要ですが、京都市民{len(citizens)}名（うち地域住民{len(residents)}名）で満たしています。", "action": ""})
        else:
            f.append({"level": "不足", "rule_id": "R2", "message": f"{n}頭（10頭以上）のため、地域住民2名を含む京都市民3名以上が必要です。現在は京都市民{len(citizens)}名、地域住民{len(residents)}名。", "action": "京都市民の活動者を追加してください。"})
    else:
        f.append({"level": "OK", "rule_id": "R2", "message": f"{n}頭（10頭未満）のため、3名要件は適用されません。", "action": ""})
    if c.get("explained_date") and c.get("consent_obtained"):
        f.append({"level": "OK", "rule_id": "R3", "message": f"町内会等への説明日 {c['explained_date']}、同意あり。申請書の同意チェック欄に記入します。", "action": ""})
    else:
        f.append({"level": "不足", "rule_id": "R3", "message": "町内会等への説明日または同意の有無が未入力です。", "action": "説明した日付と、同意を得たかを確認してください。"})
    if c.get("feeding_site") and c.get("feeding_site_is_private") and c.get("feeding_time") and c.get("toilet_site"):
        f.append({"level": "OK", "rule_id": "R4", "message": "餌場（私有地）・餌やり時間・片付け・トイレが決まっています。", "action": ""})
    elif c.get("feeding_site") and c.get("feeding_site_is_private") is False:
        f.append({"level": "注意", "rule_id": "R4", "message": "餌場が私有地ではありません。管理者の承諾など正当な権原を第6号様式に書く必要があります。", "action": "餌場の土地の管理者から承諾を得てください。"})
    else:
        f.append({"level": "不足", "rule_id": "R4", "message": "餌場・餌やり時間・トイレのいずれかが未入力です。", "action": "第6号様式の管理方法欄に必要です。確認してください。"})
    if n is not None and c.get("ear_tipped_count") is not None:
        f.append({"level": "OK", "rule_id": "R5", "message": f"頭数 {n}、耳カット済み {c['ear_tipped_count']}。手術対象は {n - c['ear_tipped_count']} 頭の見込み。", "action": ""})
    f.append({"level": "注意", "rule_id": "R6", "message": "第1号様式・第6号様式は本ツールで下書きを出力します。医療衛生センターへの提出は申請者が行います。", "action": "出力した書類を確認し、押印・提出してください。"})
    if c.get("kittens_present"):
        f.append({"level": "注意", "rule_id": "R5", "message": "子猫がいると回答されています。子猫の扱いは本ツールの範囲外です。", "action": "手術可能な月齢についてはセンターに確認してください。"})
    ready = not any(x["level"] == "不足" for x in f)
    return {"findings": f, "ready_to_apply": ready}


def _timeline_spec() -> dict:
    q = "notes.md"
    return {
        "steps": [
            {"key": "apply", "label": "登録申請書・活動実施計画書を提出", "who_decides_date": "申請者", "description": "第1号様式と第6号様式を医療衛生センターへ提出。", "documents": ["第1号様式 登録申請書", "第6号様式 活動実施計画書"], "source_quote": "医療衛生センターへ…提出"},
            {"key": "review", "label": "書類審査・現地調査", "who_decides_date": "自治体", "description": "所要日数は資料に記載なし。センターから連絡がある。", "documents": [], "source_quote": "書類審査と現地調査を経て登録"},
            {"key": "register", "label": "登録（有効3年）", "who_decides_date": "自治体", "description": "登録日から3年間有効。保護器の貸出と手術の無償実施の対象になる。", "documents": [], "source_quote": "登録の有効期間は登録日から3年間"},
            {"key": "notify", "label": "地域へのお知らせ（周知）", "who_decides_date": "申請者", "description": "捕獲の前に地域住民へ周知する。参考様式あり。", "documents": ["地域へのお知らせ（参考様式）"], "source_quote": "地域住民へ周知…したうえで捕獲"},
            {"key": "trap", "label": "捕獲（保護器貸出）", "who_decides_date": "申請者", "description": "センターから保護器を借りて捕獲。手順の指導は本ツールの範囲外。", "documents": [], "source_quote": "保護器（捕獲器）貸出"},
            {"key": "surgery", "label": "京都動物愛護センターへ持込・手術", "who_decides_date": "個別調整", "description": "手術日は登録後にセンターと個別に調整する。日数は資料に記載なし。", "documents": [], "source_quote": "手術日は登録後に個別調整"},
            {"key": "return", "label": "元の場所へ戻す", "who_decides_date": "申請者", "description": "手術後、元の場所へ戻す。", "documents": [], "source_quote": "手術後は元の場所へ戻す"},
            {"key": "annual_report", "label": "活動状況の年次報告", "who_decides_date": "規則で固定", "description": "1年ごとに活動状況（頭数の推移など）を報告する。様式は資料に記載なし。", "documents": ["活動状況報告（様式は要確認）"], "source_quote": "1年ごとに活動状況…を報告する"},
            {"key": "renewal", "label": "登録の更新申請", "who_decides_date": "規則で固定", "description": "登録から3年で更新。更新申請の提出時期は資料に記載なし。", "documents": ["更新申請（様式は要確認）"], "source_quote": "3年で更新申請"},
        ],
        "annual_report_interval_months": 12,
        "registration_validity_years": 3,
        "renewal_note": "更新申請の提出期限（登録満了の何日前か）は資料に記載なし。センターに確認。",
        "termination_note": "活動をやめるときは活動廃止届を提出する。",
        "other_deadlines": [
            {"label": "活動廃止届", "condition": "活動をやめるとき", "source_quote": "活動をやめるときは活動廃止届"},
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


def _fill(ctx, form_key: str) -> dict:
    c = ctx["colony"].to_dict()
    apply_date = ctx.get("apply_date")
    members = c.get("members") or []
    rep = members[0] if members else {}
    apply_w = _wareki(apply_date.isoformat()) if apply_date else "令和　年　月　日"
    if form_key == "registration":
        fields = [
            {"label": "申請日", "value": apply_w, "status": "記入済" if apply_date else "未入力"},
            {"label": "申請者（代表者）氏名", "value": rep.get("name", ""), "status": "記入済" if rep.get("name") else "未入力"},
            {"label": "申請者（代表者）住所", "value": rep.get("address", ""), "status": "記入済" if rep.get("address") else "未入力"},
            {"label": "申請者（代表者）電話番号", "value": rep.get("phone", ""), "status": "記入済" if rep.get("phone") else "未入力"},
            {"label": "活動場所", "value": f"京都市{c.get('ward','')}{c.get('location','')}", "status": "記入済"},
            {"label": "現在の頭数", "value": f"{c.get('cat_count')}頭（うち耳カット済み{c.get('ear_tipped_count')}頭）", "status": "記入済"},
            {"label": "活動グループ構成員", "value": "\n".join(f"{m.get('name')}（{m.get('address')}）{'地域住民' if m.get('is_resident') else '地域外'}・{'京都市民' if m.get('is_kyoto_citizen') else '市外'}" for m in members), "status": "記入済"},
            {"label": "町内会等への説明日", "value": _wareki(c.get("explained_date", "")), "status": "記入済" if c.get("explained_date") else "未入力"},
            {"label": "町内会等の名称", "value": c.get("neighborhood_association", ""), "status": "記入済"},
            {"label": "町内会等の同意", "value": "☑ 説明を行い、同意を得た" if c.get("consent_obtained") else "☐", "status": "記入済" if c.get("consent_obtained") else "未入力"},
        ]
        notes = ["令和6年4月以降、町内会長の署名欄はありません。説明日と同意チェックのみ記入します。",
                 "様式テンプレート（touroku.docx）が未配置のため、項目名は記載例に基づく暫定です。"]
        return {"form_title": "第1号様式 まちねこ活動登録申請書", "addressed_to": "京都市医療衛生センター 所長 宛", "fields": fields, "notes_for_applicant": notes}
    fields = [
        {"label": "作成日", "value": apply_w, "status": "記入済" if apply_date else "未入力"},
        {"label": "活動場所", "value": f"京都市{c.get('ward','')}{c.get('location','')}", "status": "記入済"},
        {"label": "生息状況", "value": f"約{c.get('cat_count')}頭。耳カット済み{c.get('ear_tipped_count')}頭。子猫{'あり' if c.get('kittens_present') else 'なし'}。", "status": "記入済"},
        {"label": "餌場の場所と権原", "value": f"{c.get('feeding_site','')}（{c.get('feeding_site_permission','')}）", "status": "記入済" if c.get("feeding_site_is_private") else "要確認"},
        {"label": "餌やりの方法", "value": c.get("feeding_time", ""), "status": "記入済" if c.get("feeding_time") else "未入力"},
        {"label": "トイレの設置と清掃", "value": c.get("toilet_site", ""), "status": "記入済" if c.get("toilet_site") else "未入力"},
        {"label": "不妊去勢手術の計画", "value": f"登録後、地域へ周知のうえ保護器で捕獲し、京都動物愛護センターへ持込。対象は未手術の{(c.get('cat_count') or 0) - (c.get('ear_tipped_count') or 0)}頭。手術後は元の場所へ戻す。", "status": "記入済"},
        {"label": "地域への周知方法", "value": f"{c.get('neighborhood_association','')}を通じて回覧、および餌場周辺への掲示。", "status": "要確認"},
        {"label": "活動グループの役割分担", "value": "\n".join(f"{m.get('name')}：{m.get('role')}" for m in members), "status": "記入済"},
        {"label": "活動状況の報告", "value": "登録日から1年ごとに頭数の推移を医療衛生センターへ報告する。", "status": "記入済"},
    ]
    notes = ["周知方法は記載例と照らして確認してください（回覧・掲示のどちらを行うか）。",
             "様式テンプレート（jissikeikaku.docx）が未配置のため、項目名は記載例に基づく暫定です。"]
    return {"form_title": "第6号様式 まちねこ活動実施計画書", "addressed_to": "京都市医療衛生センター 宛", "fields": fields, "notes_for_applicant": notes}


def _flyer(ctx) -> str:
    c = ctx["colony"].to_dict()
    p = ctx["profile"]
    rep = (c.get("members") or [{}])[0]
    return f"""地域の皆さまへ　―　まちねこ活動（不妊去勢手術）のお知らせ

{c.get('neighborhood_association','')}の皆さまへ

このたび、{c.get('ward','')}{c.get('location','')}周辺に生息する猫について、
京都市「{p.program_name}」の登録を受け、不妊去勢手術を行います。

■ 目的
　手術により、これ以上猫が増えないようにし、鳴き声・糞尿の苦情を減らすことを目的とします。
　手術後の猫は、目印として耳先を少しカットしたうえで、元の場所に戻します。

■ 捕獲予定期間
　{ctx.get('trap_period') or '令和　年　月　日 〜 令和　年　月　日'}
　（期間中、保護器（捕獲かご）を設置します。かごに触れないようお願いします）

■ 飼い猫をお飼いの方へ
　誤って捕獲しないため、期間中は首輪を付ける、または屋内で過ごさせるようお願いします。
　万一捕獲された場合は下記へご連絡ください。

■ 餌やりについて
　餌やりは活動グループが決めた場所・時間で行い、片付けまで行います。
　それ以外の場所での餌やりは、捕獲の妨げになるためお控えください。

■ 連絡先
　活動グループ代表：{rep.get('name','')}（{rep.get('phone','')}）
　京都市{p.office}：{'／'.join(p.contacts)}

この活動は京都市の事業として、活動グループが地域の同意を得て行うものです。
"""


def _intake(ctx) -> dict:
    """台本どおりに進む聞き取り。ユーザーの発言内容は読まず、サンプルコロニーを段階的に埋める。"""
    colony = ctx["colony"].to_dict()
    turn = len([m for m in ctx["history"] if m["role"] == "user"])
    s = SAMPLE
    if turn <= 1:
        patch = {k: s[k] for k in ("ward", "location", "cat_count", "ear_tipped_count", "kittens_present")}
        reply = (f"承知しました。{s['ward']}{s['location']}、現在{s['cat_count']}頭、うち耳カット済み{s['ear_tipped_count']}頭、子猫なし、で記録します。\n\n"
                 "次に管理方法を伺います。餌場はどこですか。その土地は私有地ですか（誰の敷地・承諾か）。餌やりの時間帯と、食べ残しの片付け方も教えてください。")
        return {"reply": reply, "colony_patch": patch, "complete": False}
    if turn == 2:
        patch = {k: s[k] for k in ("feeding_site", "feeding_site_is_private", "feeding_site_permission", "feeding_time", "toilet_site")}
        reply = (f"餌場は{s['feeding_site']}（{s['feeding_site_permission']}）、{s['feeding_time']}。トイレは{s['toilet_site']}、で記録します。\n\n"
                 "次に地域の合意です。町内会等の名称、説明を行った日付、同意を得られたかを教えてください。")
        return {"reply": reply, "colony_patch": patch, "complete": False}
    if turn == 3:
        patch = {k: s[k] for k in ("neighborhood_association", "explained_date", "consent_obtained")}
        reply = (f"{s['neighborhood_association']}に{s['explained_date']}に説明し、同意あり、で記録します。\n\n"
                 "最後に活動者です。一緒に活動する方の氏名・住所・電話番号と、その方が活動場所の地域住民か、京都市民かを、全員分教えてください。"
                 f"頭数が{s['cat_count']}頭（10頭以上）なので、地域住民2名を含む京都市民3名以上が必要です。")
        return {"reply": reply, "colony_patch": patch, "complete": False}
    patch = {"members": s["members"], "notes": s["notes"]}
    names = "、".join(m["name"] for m in s["members"])
    reply = (f"活動者3名（{names}）を記録しました。地域住民2名・京都市民3名で、10頭以上の要件を満たします。\n\n"
             "聞き取りは以上です。左のメニューから「2. 要綱照合」に進んでください。")
    return {"reply": reply, "colony_patch": patch, "complete": True}


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
    raise KeyError(f"mock: unknown task {task}")
