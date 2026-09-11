"""ネコノテ — Streamlit UI。

サイドバーで「市民面」と「自治体面」を切り替える。市民面は 1→5→7 の工程、自治体面は台帳。
永続化は台帳（JSON）のみ。ほかは st.session_state。
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import streamlit as st

from machineko import documents, flyer, intake, next_actions, report, rules, schedule, ui
from machineko.colony import Colony
from machineko.llm import LLM
from machineko.profile import list_municipalities, load_profile
from machineko.registry import Registry

st.set_page_config(page_title="ネコノテ", page_icon="📋", layout="wide")
ui.inject()

# ---------- state ----------
ss = st.session_state
ss.setdefault("municipality", "kyoto")
ss.setdefault("mode", "citizen")
ss.setdefault("step", 1)
ss.setdefault("colony", Colony())
ss.setdefault("chat", [])
ss.setdefault("intake_complete", False)
ss.setdefault("rules", None)
ss.setdefault("findings", None)
ss.setdefault("timeline_spec", None)
ss.setdefault("anchors", {"apply": dt.date.today() + dt.timedelta(days=7), "register": None, "notify": None, "trap": None, "surgery": None, "return_": None})
ss.setdefault("forms", {})
ss.setdefault("flyer", None)
ss.setdefault("submitted_id", None)
ss.setdefault("notified", False)
ss.setdefault("report_chat", [])
ss.setdefault("report_draft", None)
ss.setdefault("report_done", False)


@st.cache_resource
def get_llm() -> LLM:
    return LLM()


@st.cache_resource
def get_profile(mid: str):
    return load_profile(mid)


@st.cache_resource
def get_registry(mid: str) -> Registry:
    return Registry(mid)


llm = get_llm()
profile = get_profile(ss.municipality)
registry = get_registry(ss.municipality)


def reset_derived():
    ss.findings = None
    ss.forms = {}
    ss.flyer = None


def reset_all(keep_mid: str):
    for k in list(ss.keys()):
        del ss[k]
    ss.municipality = keep_mid


STEPS = ["聞き取り", "要綱照合", "書類出力", "周知チラシ", "日程表", "報告"]
STEP_NO = [1, 2, 3, 4, 5, 7]


def step_done(n: int) -> bool:
    return {1: ss.intake_complete, 2: ss.findings is not None, 3: ss.submitted_id is not None, 4: ss.flyer is not None, 5: ss.timeline_spec is not None, 7: ss.report_done}.get(n, False)


# ---------- sidebar ----------
with st.sidebar:
    st.markdown('<div style="font-size:20px;font-weight:700;margin-bottom:2px">ネコノテ</div><div style="font-size:12px;color:#AAB4BE;margin-bottom:14px">受付も報告も更新も落とさず回せて、担い手が代わっても市に情報が残る</div>', unsafe_allow_html=True)
    mids = list_municipalities()
    mid = st.selectbox("自治体プロファイル", mids, index=mids.index(ss.municipality), format_func=lambda m: get_profile(m).name)
    if mid != ss.municipality:
        reset_all(mid)
        st.rerun()
    mode = st.radio("画面", ["citizen", "city"], format_func=lambda m: "市民面（活動者）" if m == "citizen" else "自治体面（窓口）", horizontal=True, index=0 if ss.mode == "citizen" else 1)
    ss.mode = mode
    if mode == "citizen":
        st.markdown('<div style="font-size:12px;color:#AAB4BE;margin:10px 0 4px">工程</div>', unsafe_allow_html=True)
        cur = STEP_NO.index(ss.step) if ss.step in STEP_NO else 0
        ss.step = st.radio("工程", STEP_NO, index=cur, label_visibility="collapsed", key="step_radio",
                           format_func=lambda n: f"{'✓' if step_done(n) else '　'} {STEP_NO.index(n) + 1}. {STEPS[STEP_NO.index(n)]}")
    st.divider()
    st.caption(f"LLM：{llm.mode_label}")
    avail = [s for s in profile.sources if s.available]
    with st.expander(f"読み込んだ一次資料 {len(avail)}件"):
        for s in avail:
            st.markdown(f"- `{s.file}`  \n<span style='font-size:12px;color:#AAB4BE'>{s.role}</span>", unsafe_allow_html=True)
    missing = profile.missing_sources()
    if missing:
        with st.expander(f"読めない・未配置の資料 {len(missing)}件"):
            for s in missing:
                st.markdown(f"- `{s.file}` — {s.role}")
    st.divider()
    if st.button("デモ用のコロニー情報を読み込む", use_container_width=True):
        sample = Path("demo") / f"sample_colony_{profile.id}.json"
        if not sample.exists():
            sample = Path("demo") / "sample_colony.json"
        ss.colony = Colony.from_dict(json.loads(sample.read_text(encoding="utf-8")))
        ss.intake_complete = True
        ss.chat = [{"role": "assistant", "content": "デモ用のコロニー情報を読み込みました。右側に内容を表示しています。"}]
        reset_derived()
        st.rerun()
    if st.button("すべてリセット（台帳もデモ初期状態に戻す）", use_container_width=True):
        registry.reset()
        reset_all(ss.municipality)
        st.rerun()

ui.header(profile, ss.mode)


def render_next_actions():
    rec = registry.get(ss.submitted_id) if ss.submitted_id else None
    d = registry.deadlines(rec) if rec else None
    acts = next_actions.next_actions(
        spec=ss.timeline_spec, intake_complete=ss.intake_complete, findings=ss.findings, forms_done=set(ss.forms.keys()),
        record=rec, deadlines=d, notified=ss.notified or ss.flyer is not None, surgery_form_done="surgery" in ss.forms,
    )
    ui.next_actions_card(acts, rec, d["status"] if d else None, ss.timeline_spec is not None)


def chat_turn(history_key: str, fn, *, disabled: bool):
    """チャット入力1回分。fn(history) -> out。"""
    user_text = st.chat_input("回答を入力", disabled=disabled)
    if not user_text:
        return None
    ss[history_key].append({"role": "user", "content": user_text})
    hist = [m for m in ss[history_key] if m["role"] in ("user", "assistant")]
    first_user = next(i for i, m in enumerate(hist) if m["role"] == "user")
    with st.spinner("整理しています…"):
        try:
            return fn(hist[first_user:])
        except Exception as e:  # noqa: BLE001
            st.error(f"LLM 呼び出しに失敗しました: {e}")
            st.stop()


# ======================================================================
# 自治体面
# ======================================================================
if ss.mode == "city":
    rows = registry.rows()
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["状態"]] = counts.get(r["状態"], 0) + 1
    cols = st.columns(max(len(counts), 1))
    for (k, v), c in zip(counts.items(), cols):
        with c:
            ui.stat(k, f"{v} 件", red=(k == "期限超過"))
    st.markdown("")
    status_col = "状態"
    st.dataframe(
        rows, use_container_width=True, hide_index=True,
        column_config={status_col: st.column_config.TextColumn(status_col)},
    )
    st.caption("並び順：期限超過 → 報告待ち → 更新待ち → 申請中 → 交付済／報告済 → 登録済。「期限超過」のうち届出が無いものは、この一覧が無ければ理由が残らない地域です。")
    ids = [r["ID"] for r in rows]
    default = ids.index(ss.submitted_id) if ss.submitted_id in ids else 0
    cid = st.selectbox("詳細を見るコロニー", ids, index=default, format_func=lambda i: f"{i}　{registry.get(i)['ward']}{registry.get(i).get('town', '')} {registry.get(i)['location']}")
    rec = registry.get(cid)
    d = registry.deadlines(rec)
    is_ticket = rec.get("kind") == "ticket"
    st.markdown(f'<div class="mk-title" style="margin-top:8px">{ui.e(rec["id"])}　{ui.e(rec["ward"])}{ui.e(rec.get("town", ""))}　<span style="font-weight:500;color:#5B6570">{ui.e(rec["location"])}</span>　{ui.badge(d["status"])}</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.stat("代表者", rec.get("representative") or "—")
    with c2:
        ui.stat("頭数／手術済", f"{rec['cat_count']}／{rec['ear_tipped_count']}")
    if is_ticket:
        with c3:
            ui.stat("報告期限（有効月末）", d["next_report_due"].isoformat() if d["next_report_due"] else "—", f"有効期間 {rec.get('ticket_valid_from')} 〜")
        with c4:
            ui.stat("チケット枚数", str(rec.get("tickets") or "—"))
    else:
        rules_ = rec.get("rules") or {}
        with c3:
            ui.stat("次回報告期限", d["next_report_due"].isoformat() if d["next_report_due"] else "—",
                    f"基準日 {d['next_report_base']} から {rules_.get('annual_report_window_days')} 日以内" if d["next_report_base"] else "")
        with c4:
            ui.stat("更新満了日", d["renewal_due"].isoformat() if d["renewal_due"] else "—",
                    f"更新申請は {d['renewal_open']} から" if d["renewal_open"] else "")
    if d["status"] == "更新待ち":
        st.warning(f"更新申請の受付期間です（{d['renewal_open']} 〜 {d['renewal_due']}）。更新申請書と実施計画書の提出が必要です。")
    if d["status"] == "期限超過":
        st.error("期限を過ぎています。届出が無ければ理由は残りません。活動者に連絡してください。")
    if not rec.get("registered_date"):
        with st.container(border=True):
            st.markdown("**職員の操作**　" + ("基金からチケットが届いたら交付日を入れます。" if is_ticket else "書類審査・現地調査が済んだら登録します。"))
            if is_ticket:
                st.caption(f"有効期間 {rec.get('ticket_valid_from')} 〜 {rec.get('ticket_valid_until')}／申請枚数 {rec.get('tickets')}")
            reg_date = st.date_input("交付日" if is_ticket else "登録日", value=dt.date.today(), key="reg_date")
            if st.button("チケットを交付する" if is_ticket else "登録する", type="primary"):
                registry.register(cid, reg_date)
                st.rerun()
    tab1, tab2 = st.tabs(["提出された申請書類", f"報告（{len(rec.get('reports', []))}件）"])
    with tab1:
        if not rec.get("documents"):
            st.caption("（ダミーデータのため書類は未登録）")
        for key, doc in rec.get("documents", {}).items():
            st.markdown(f"**{doc['form_title']}**")
            ui.fields_table(doc["fields"])
    with tab2:
        if not rec.get("reports"):
            st.caption("報告はまだありません。")
        for rp in sorted(rec.get("reports", []), key=lambda r: r["date"], reverse=True):
            st.markdown(f'<div class="mk-card soft"><b>{ui.e(rp["date"])}</b>　頭数 {ui.e(rp["cat_count"])}／手術済 {ui.e(rp["ear_tipped_count"])}／手術 {ui.e(rp.get("surgeries", "—"))} 頭<div style="font-size:13.5px;margin-top:4px">{ui.e(rp["summary"])}</div></div>', unsafe_allow_html=True)
    st.stop()

# ======================================================================
# 市民面
# ======================================================================
render_next_actions()
step = ss.step

# ---------- 1. 聞き取り ----------
if step == 1:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("1. 聞き取り")
        st.caption("様式に必要な項目を会話で集めます。分かる範囲で答えてください。")
        if not ss.chat:
            ss.chat.append({"role": "assistant", "content": "申請に必要な情報を伺います。まず、猫がいる場所（区・町名・目印）と、今分かっている頭数を教えてください。耳カット済みの猫がいれば、その数も。"})
        for m in ss.chat:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        out = chat_turn("chat", lambda h: intake.intake_turn(llm, profile, ss.colony, h), disabled=ss.intake_complete)
        if out:
            ss.colony = ss.colony.merge(out["colony_patch"])
            reset_derived()
            ss.chat.append({"role": "assistant", "content": out["reply"]})
            if out["complete"]:
                ss.intake_complete = True
            st.rerun()
        if ss.intake_complete:
            st.success("聞き取り完了。「2. 要綱照合」へ進んでください。")
            if st.button("聞き取りを再開する"):
                ss.intake_complete = False
                st.rerun()
    with right:
        ui.colony_summary(ss.colony.summary_lines())
        with st.expander("JSON"):
            st.code(ss.colony.to_json(), language="json")

# ---------- 2. 要綱照合 ----------
elif step == 2:
    st.subheader("2. 要綱照合")
    st.caption(f"{profile.name}の一次資料から規則を抽出し、コロニー情報を照らします。規則はコードに書かず、資料から毎回読みます。")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("① 要綱から規則を抽出", use_container_width=True):
            with st.spinner("一次資料を読んでいます…"):
                ss.rules = rules.extract_rules(llm, profile)
            ss.findings = None
    with c2:
        if st.button("② コロニー情報を照合", type="primary", disabled=ss.rules is None, use_container_width=True):
            with st.spinner("照合しています…"):
                ss.findings = rules.check_colony(llm, profile, ss.rules, ss.colony)
    if ss.findings:
        ui.findings(ss.findings["findings"], ss.findings["ready_to_apply"])
    if ss.rules:
        with st.expander(f"抽出した規則 {len(ss.rules)} 件（根拠付き）", expanded=ss.findings is None):
            ui.rules_list(ss.rules)
    with st.expander("コロニー情報"):
        ui.colony_summary(ss.colony.summary_lines())

# ---------- 3. 書類出力 ----------
elif step == 3:
    st.subheader("3. 書類出力")
    st.caption("様式の項目名と記載例を一次資料から読み、コロニー情報を転記します。配布様式の DOCX があればそのセルに直接埋めます。")
    apply_date = st.date_input("申請日", value=ss.anchors["apply"] or dt.date.today())
    ss.anchors["apply"] = apply_date
    tabs = st.tabs([("✓ " if k in ss.forms else "") + f["label"] for k, f in profile.forms.items()])
    for (key, form), tab in zip(profile.forms.items(), tabs):
        with tab:
            tpl = profile.template_path(key)
            if form.get("after_registration"):
                st.caption("登録後に提出する様式。配布 DOCX が無いので資料の様式に沿って生成します。手術を申請する猫を入力してください。")
                n_default = max((ss.colony.cat_count or 0) - (ss.colony.ear_tipped_count or 0), 1)
                rows_ = ss.colony.cats or [{"color": "", "sex": "不明", "features": ""} for _ in range(n_default)]
                edited = st.data_editor(rows_, num_rows="dynamic", key=f"cats_{key}", use_container_width=True,
                                        column_config={"color": "毛色", "sex": st.column_config.SelectboxColumn("性別", options=["オス", "メス", "不明"]), "features": "特徴"})
                ss.colony.cats = [dict(r) for r in edited]
            else:
                st.caption("配布様式の DOCX のセルに直接転記します。" if tpl else "配布様式が無いため資料の項目に沿って生成します。")
            done = key in ss.forms
            b1, b2, _ = st.columns([1, 1, 3])
            with b1:
                if st.button("作成" if not done else "作り直す", key=f"make_{key}", use_container_width=True, type="primary" if not done else "secondary"):
                    with st.spinner("記入しています…"):
                        filled = documents.fill_form_fields(llm, profile, ss.colony, key, apply_date)
                        data, how = documents.render_docx(profile, key, filled)
                    ss.forms[key] = {"filled": filled, "docx": data, "how": how}
                    st.rerun()
            with b2:
                if done:
                    st.download_button("DOCX をダウンロード", data=ss.forms[key]["docx"], file_name=f"{key}_{apply_date.isoformat()}.docx",
                                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_{key}", use_container_width=True)
            if done:
                fm = ss.forms[key]
                st.caption(fm["how"])
                ui.fields_table(fm["filled"]["fields"])
                if fm["filled"]["notes_for_applicant"]:
                    st.info("\n".join(f"- {n}" for n in fm["filled"]["notes_for_applicant"]))
    st.markdown("")
    both = all(k in ss.forms for k, f in profile.forms.items() if not f.get("after_registration"))
    if ss.submitted_id:
        st.success(f"提出済み。台帳ID {ss.submitted_id}。自治体面の一覧に載っています。")
    else:
        with st.container(border=True):
            st.markdown(f"**提出**　申請時の様式が揃ったら{profile.office}へ提出します。台帳に「申請中」として載ります。")
            if st.button(f"{profile.office}へ提出", type="primary", disabled=not both):
                if ss.timeline_spec is None:
                    with st.spinner("報告・更新の期限を要綱から読んでいます…"):
                        ss.timeline_spec = schedule.extract_timeline_spec(llm, profile)
                rec = registry.submit_application(
                    ss.colony.to_dict(),
                    {k: v["filled"] for k, v in ss.forms.items() if not profile.forms[k].get("after_registration")},
                    apply_date, ss.timeline_spec,
                )
                ss.submitted_id = rec["id"]
                st.rerun()

# ---------- 4. 周知チラシ ----------
elif step == 4:
    st.subheader("4. 周知チラシ（地域へのお知らせ）")
    st.caption("参考様式に沿って本文を作ります。捕獲の前に配布・掲示するものです。")
    a = ss.anchors
    period = f"{a['trap'].isoformat()} 〜" if a.get("trap") else ""
    period = st.text_input("捕獲予定期間（空欄なら記入欄のまま）", value=period)
    if st.button("作成", type="primary"):
        with st.spinner("作成しています…"):
            ss.flyer = flyer.generate_flyer(llm, profile, ss.colony, period)
            ss.notified = True
    if ss.flyer:
        st.text_area("本文", ss.flyer, height=520)
        st.download_button("テキストをダウンロード", data=ss.flyer.encode("utf-8"), file_name="osirase.txt", mime="text/plain")

# ---------- 5. 日程表 ----------
elif step == 5:
    st.subheader("5. 日程表")
    st.caption("工程の並びと期限は一次資料から抽出します。日付の計算はコード側です。資料に日数の記載が無いものは「記載なし」と出します。")
    if ss.timeline_spec is None:
        if st.button("要綱から工程と期限を抽出", type="primary"):
            with st.spinner("一次資料を読んでいます…"):
                ss.timeline_spec = schedule.extract_timeline_spec(llm, profile)
            st.rerun()
    else:
        spec = ss.timeline_spec
        w = spec.get("application_window")
        if w:
            st.markdown("**最短日程（受付期間から計算）**")
            ready = st.date_input("準備完了日（申請書類が揃う日）", value=dt.date.today(), key="ready_date")
            e_ = schedule.earliest_schedule(spec, ready)
            c1, c2, c3 = st.columns(3)
            with c1:
                ui.stat("最短の申請日", e_["apply"].isoformat())
            with c2:
                ui.stat("チケット有効期間", f"{e_['valid_from']} 〜 {e_['valid_until']}", f"準備完了から {e_['wait_days']} 日")
            with c3:
                ui.stat("この受付を逃すと", f"+{e_['delay_days']} 日", f"次の申請 {e_['missed_apply']}、有効 {e_['missed_valid_from']} から", red=True)
            st.caption(f"受付：毎月{w['from_day']}日〜{w['to_day'] or '末'}日、交付は申請月の{w['ticket_month_offset']}か月後の分、{w['valid_months']}か月有効"
                       + (f"、上限{w['max_tickets']}枚" if w.get("max_tickets") else "") + "。出典：「" + w["source_quote"] + "」　規則で決まる待ちは消せません。消せるのは、受付を逃す・報告を落とす・書類の不備で戻される、の3つです。")
        else:
            st.caption("この制度には受付期間の定め（毎月◯日〜、翌月分など）がありません。審査・現地調査の日数は自治体の裁量で、資料に記載がありません。")
        st.markdown("**基準日**　決まっているものだけ入力。登録日を入れると報告と更新の期限が出ます。")
        a = ss.anchors
        c = st.columns(6)
        labels = [("apply", "申請日"), ("register", "登録日"), ("notify", "周知日"), ("trap", "捕獲日"), ("surgery", "持込日"), ("return_", "リターン日")]
        for (k, lab), col in zip(labels, c):
            with col:
                on = st.checkbox(lab, value=a.get(k) is not None, key=f"on_{k}")
                a[k] = st.date_input(lab, value=a.get(k) or a.get("apply") or dt.date.today(), key=f"d_{k}", label_visibility="collapsed") if on else None
        if ss.submitted_id and (rec := registry.get(ss.submitted_id)) and rec.get("registered_date"):
            a["register"] = dt.date.fromisoformat(rec["registered_date"])
            st.caption(f"登録日は台帳（{ss.submitted_id}）の値を使っています。")
        rows_ = schedule.build_timeline(spec, schedule.Anchors(**a))
        ui.timeline(rows_)
        st.info(f"更新：{spec['renewal_note']}  \n終了時：{spec['termination_note']}")
        if spec.get("other_deadlines"):
            with st.expander("条件付きで発生する提出物"):
                for d_ in spec["other_deadlines"]:
                    st.markdown(f"- **{d_['label']}**　{d_['condition']}　<span style='color:#5B6570;font-size:12.5px'>「{d_['source_quote']}」</span>", unsafe_allow_html=True)
        with st.expander("抽出元の引用"):
            for s in spec["steps"]:
                st.markdown(f"- {s['label']}：「{s['source_quote']}」")

# ---------- 7. 報告 ----------
elif step == 7:
    rep_label = next((s["label"] for s in (ss.timeline_spec or {}).get("steps", []) if s["key"] == "annual_report"), "報告")
    st.subheader(f"6. 報告：{rep_label}")
    st.caption("会話で内容を集めて報告書にし、提出すると自治体面の状態が変わります。")
    registered = [r for r in registry.all() if r.get("registered_date")]
    if not registered:
        st.warning("登録（交付）済みのコロニーがありません。自治体面で登録してください。")
        st.stop()
    ids = [r["id"] for r in registered]
    default = ids.index(ss.submitted_id) if ss.submitted_id in ids else 0
    cid = st.selectbox("報告するコロニー", ids, index=default, format_func=lambda i: f"{i}　{registry.get(i)['ward']}{registry.get(i).get('town', '')} {registry.get(i)['location']}")
    if ss.get("report_cid") != cid:
        ss.report_cid = cid
        ss.report_chat, ss.report_draft, ss.report_done = [], None, False
    rec = registry.get(cid)
    d = registry.deadlines(rec)
    st.markdown(f"状態：{ui.badge(d['status'])}　次回報告：基準日 {d['next_report_base'] or '—'} ／ 期限 **{d['next_report_due'] or '—'}**", unsafe_allow_html=True)
    if ss.report_done:
        st.success("提出しました。自治体面で状態を確認できます。")
        if ss.get("report_docx"):
            st.download_button("報告書 DOCX をダウンロード", data=ss.report_docx, file_name=f"houkoku_{cid}_{dt.date.today().isoformat()}.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.stop()
    if not ss.report_chat:
        ss.report_chat.append({"role": "assistant", "content": f"{rep_label}を受け付けます。前回時点は{rec.get('cat_count')}頭（手術済{rec.get('ear_tipped_count')}頭）でした。現在管理する猫の頭数と、うち手術済の頭数を教えてください。"})
    for m in ss.report_chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if ss.report_draft:
        rp = ss.report_draft
        with st.container(border=True):
            st.markdown(f"**報告書の内容**　現在管理する猫 {rp['cat_count']}頭／うち手術済 {rp['ear_tipped_count']}頭／手術 {rp['surgeries']}頭  \n{rp['summary']}")
            if st.button(f"{profile.office}へ提出", type="primary"):
                today = dt.date.today()
                registry.submit_report(cid, {"date": today.isoformat(), **rp})
                ss.report_docx = report.build_report_docx(profile, rec, rp, today, ss.timeline_spec)
                ss.report_done = True
                st.rerun()
    out = chat_turn("report_chat", lambda h: report.report_turn(llm, profile, rec, h), disabled=ss.report_draft is not None)
    if out:
        ss.report_chat.append({"role": "assistant", "content": out["reply"]})
        if out["complete"] and out["report"]:
            ss.report_draft = out["report"]
        st.rerun()
