"""まちねこ事務局AI — Streamlit UI。

左のメニューが完成の定義（HANDOFF §6-3）の 1→6 に対応する。
永続化はしない。全部 st.session_state に置く。
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import streamlit as st

from machineko import documents, flyer, intake, next_actions, report, rules, schedule
from machineko.registry import Registry
from machineko.colony import Colony
from machineko.llm import LLM
from machineko.profile import list_municipalities, load_profile

st.set_page_config(page_title="まちねこ事務局AI", page_icon="📋", layout="wide")

# ---------- state ----------
ss = st.session_state
ss.setdefault("municipality", "kyoto")
ss.setdefault("colony", Colony())
ss.setdefault("chat", [])            # [{"role","content"}]
ss.setdefault("intake_complete", False)
ss.setdefault("rules", None)
ss.setdefault("findings", None)
ss.setdefault("timeline_spec", None)
ss.setdefault("anchors", {"apply": dt.date.today() + dt.timedelta(days=7), "register": None, "notify": None, "trap": None, "surgery": None, "return_": None})
ss.setdefault("forms", {})           # form_key -> {"filled":..., "docx":bytes, "how":str}
ss.setdefault("flyer", None)
ss.setdefault("submitted_id", None)   # 提出済みならその台帳ID
ss.setdefault("report_chat", [])
ss.setdefault("report_draft", None)
ss.setdefault("report_done", False)
ss.setdefault("notified", False)


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
    """コロニー情報が変わったら、それに依存する結果を消す。"""
    ss.findings = None
    ss.forms = {}
    ss.flyer = None


# ---------- sidebar ----------
with st.sidebar:
    st.title("まちねこ事務局AI")
    st.caption("地域猫活動の申請・計画書・日程・報告の事務を引き受けます。")
    mids = list_municipalities()
    mid = st.selectbox("自治体プロファイル", mids, index=mids.index(ss.municipality))
    if mid != ss.municipality:
        for k in list(ss.keys()):
            del ss[k]
        ss.municipality = mid
        st.rerun()
    step = st.radio(
        "工程",
        ["1. 聞き取り", "2. 要綱照合", "3. 書類出力", "4. 周知チラシ", "5. 日程表", "6. 自治体面：登録コロニー一覧", "7. 報告"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"LLM：{llm.mode_label}")
    avail = [s.file for s in profile.sources if s.available]
    missing = profile.missing_sources()
    with st.expander(f"読み込んだ一次資料 {len(avail)}件"):
        for s in profile.sources:
            if s.available:
                st.markdown(f"- `{s.file}` — {s.role}")
    if missing:
        with st.expander(f"読めない・未配置の資料 {len(missing)}件"):
            for s in missing:
                st.markdown(f"- `{s.file}` — {s.role}")
            st.caption("画像だけの PDF はテキストが取れないため LLM に渡していません。")
    st.divider()
    if st.button("デモ用のコロニー情報を読み込む", use_container_width=True):
        sample = Path("demo") / f"sample_colony_{profile.id}.json"
        if not sample.exists():
            sample = Path("demo") / "sample_colony.json"
        ss.colony = Colony.from_dict(json.loads(sample.read_text(encoding="utf-8")))
        ss.intake_complete = True
        ss.chat = [{"role": "assistant", "content": "デモ用のコロニー情報を読み込みました。内容は右側に表示しています。"}]
        reset_derived()
        st.rerun()
    if st.button("すべてリセット（台帳もデモ初期状態に戻す）", use_container_width=True):
        registry.reset()
        keep = ss.municipality
        for k in list(ss.keys()):
            del ss[k]
        ss.municipality = keep
        st.rerun()

# ---------- header ----------
st.markdown(f"#### {profile.name}　{profile.program_name}")
st.caption("対象：地域の同意が済んだ後 〜 完了報告まで。捕獲の手順・自治会への説得・里親探し・子猫の育て方は扱いません。担い手を増やさず、制度と担い手の間の時間と引継ぎの摩擦だけを消します。")


def next_actions_card():
    """市民面の先頭に出す1枚。要綱から抽出した工程と台帳の状態から組み立てる。"""
    rec = registry.get(ss.submitted_id) if ss.submitted_id else None
    d = registry.deadlines(rec) if rec else None
    acts = next_actions.next_actions(
        spec=ss.timeline_spec, intake_complete=ss.intake_complete, findings=ss.findings, forms_done=set(ss.forms.keys()),
        record=rec, deadlines=d, notified=ss.notified or ss.flyer is not None, surgery_form_done="surgery" in ss.forms,
    )
    icon = {"now": "🔴", "soon": "🟡", "wait": "⏳", "late": "‼️"}
    with st.container(border=True):
        st.markdown("**次にやること**" + (f"　<small>台帳ID {rec['id']}／状態 {d['status']}</small>" if rec else ""), unsafe_allow_html=True)
        for x in acts:
            due = f"　期限 **{x['due']}**" if x["due"] else ""
            docs = f"　提出物：{'、'.join(x['docs'])}" if x["docs"] else ""
            st.markdown(f"{icon[x['level']]} {x['title']}{due}  \n<small>{x['note']}{docs}</small>", unsafe_allow_html=True)
        if ss.timeline_spec is None:
            st.caption("要綱から工程を抽出すると、様式名と期限が入ります（5. 日程表）。")


def colony_panel():
    st.markdown("**コロニー情報**")
    for line in ss.colony.summary_lines():
        st.markdown(line)
    with st.expander("JSON"):
        st.code(ss.colony.to_json(), language="json")


if not step.startswith("6."):
    next_actions_card()

# ---------- 1. 聞き取り ----------
if step.startswith("1."):
    left, right = st.columns([3, 2])
    with left:
        st.subheader("1. 聞き取り")
        if not ss.chat:
            ss.chat.append({"role": "assistant", "content": "申請に必要な情報を伺います。まず、猫がいる場所（区・町名・目印）と、今分かっている頭数を教えてください。耳カット済みの猫がいれば、その数も。"})
        for m in ss.chat:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        user_text = st.chat_input("回答を入力", disabled=ss.intake_complete)
        if user_text:
            ss.chat.append({"role": "user", "content": user_text})
            history = [m for m in ss.chat if m["role"] in ("user", "assistant")]
            # 先頭が assistant の挨拶なので、API に渡す履歴は最初の user から
            first_user = next(i for i, m in enumerate(history) if m["role"] == "user")
            history = history[first_user:]
            with st.spinner("整理しています…"):
                try:
                    out = intake.intake_turn(llm, profile, ss.colony, history)
                except Exception as e:
                    st.error(f"LLM 呼び出しに失敗しました: {e}")
                    st.stop()
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
        colony_panel()

# ---------- 2. 要綱照合 ----------
elif step.startswith("2."):
    st.subheader("2. 要綱照合")
    st.caption(f"{profile.name}の一次資料から規則を抽出し、コロニー情報を照らします。規則はコードに書かず、資料から毎回読みます。")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("要綱から規則を抽出", type="secondary"):
            with st.spinner("一次資料を読んでいます…"):
                ss.rules = rules.extract_rules(llm, profile)
            ss.findings = None
    with c2:
        if st.button("コロニー情報を照合", type="primary", disabled=ss.rules is None):
            with st.spinner("照合しています…"):
                ss.findings = rules.check_colony(llm, profile, ss.rules, ss.colony)
    if ss.rules:
        with st.expander(f"抽出した規則 {len(ss.rules)}件（根拠付き）", expanded=ss.findings is None):
            for r in ss.rules:
                st.markdown(f"**{r['id']}**［{r['category']}］{r['requirement']}  \n<small>適用：{r['applies_when']}／出典：`{r['source_file']}`「{r['source_quote']}」</small>", unsafe_allow_html=True)
    if ss.findings:
        f = ss.findings
        order = {"不足": 0, "注意": 1, "OK": 2}
        items = sorted(f["findings"], key=lambda x: order.get(x["level"], 9))
        n_lack = sum(1 for x in items if x["level"] == "不足")
        n_warn = sum(1 for x in items if x["level"] == "注意")
        if f["ready_to_apply"]:
            st.success(f"不足なし（注意 {n_warn}件）。申請できます。")
        else:
            st.error(f"不足 {n_lack}件、注意 {n_warn}件。申請前に解消してください。")
        for x in items:
            icon = {"不足": "🔴", "注意": "🟡", "OK": "🟢"}[x["level"]]
            body = f"{icon} **{x['level']}**（{x['rule_id']}）{x['message']}"
            if x["action"]:
                body += f"  \n→ {x['action']}"
            st.markdown(body)
    st.divider()
    colony_panel()

# ---------- 3. 書類出力 ----------
elif step.startswith("3."):
    st.subheader("3. 書類出力")
    st.caption("様式の項目名と記載例を一次資料から読み、コロニー情報を転記します。配布様式の DOCX が sources/ にあればそこに直接埋めます。")
    apply_date = st.date_input("申請日", value=ss.anchors["apply"] or dt.date.today())
    ss.anchors["apply"] = apply_date
    cols = st.columns(len(profile.forms))
    for (key, form), col in zip(profile.forms.items(), cols):
        with col:
            st.markdown(f"**{form['label']}**")
            tpl = profile.template_path(key)
            if form.get("after_registration"):
                st.caption("登録後に提出する様式。配布DOCXが無いので要綱の様式に沿って生成")
                n_default = max((ss.colony.cat_count or 0) - (ss.colony.ear_tipped_count or 0), 1)
                rows = ss.colony.cats or [{"color": "", "sex": "不明", "features": ""} for _ in range(n_default)]
                edited = st.data_editor(rows, num_rows="dynamic", key=f"cats_{key}", use_container_width=True,
                                        column_config={"color": "毛色", "sex": st.column_config.SelectboxColumn("性別", options=["オス", "メス", "不明"]), "features": "特徴"})
                ss.colony.cats = [dict(r) for r in edited]
            else:
                st.caption("配布様式に転記" if tpl else "配布様式が未配置のため代替生成")
            if st.button("作成", key=f"make_{key}"):
                with st.spinner("記入しています…"):
                    filled = documents.fill_form_fields(llm, profile, ss.colony, key, apply_date)
                    data, how = documents.render_docx(profile, key, filled)
                ss.forms[key] = {"filled": filled, "docx": data, "how": how}
            if key in ss.forms:
                fm = ss.forms[key]
                st.download_button("DOCX をダウンロード", data=fm["docx"], file_name=f"{key}_{apply_date.isoformat()}.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_{key}")
                st.caption(fm["how"])
                st.markdown(f"**{fm['filled']['form_title']}**　{fm['filled']['addressed_to']}")
                for fld in fm["filled"]["fields"]:
                    mark = {"記入済": "", "要確認": " 🟡要確認", "未入力": " 🔴未入力"}[fld["status"]]
                    st.markdown(f"- {fld['label']}{mark}  \n　{fld['value'] or '（空欄）'}".replace("\n　", "\n　").replace("\n", "  \n"))
                if fm["filled"]["notes_for_applicant"]:
                    st.info("\n".join(f"- {n}" for n in fm["filled"]["notes_for_applicant"]))
    st.divider()
    both = all(k in ss.forms for k, f in profile.forms.items() if not f.get("after_registration"))
    if ss.submitted_id:
        st.success(f"提出済み。台帳ID {ss.submitted_id}。「6. 自治体面」で一覧に載っています。")
    else:
        st.markdown("**提出**　2様式が揃ったら医療衛生センターへ提出します（台帳に「申請中」として載ります）。")
        if st.button("医療衛生センターへ提出", type="primary", disabled=not both):
            if ss.timeline_spec is None:
                with st.spinner("報告・更新の期限を要綱から読んでいます…"):
                    ss.timeline_spec = schedule.extract_timeline_spec(llm, profile)
            rec = registry.submit_application(ss.colony.to_dict(), {k: v["filled"] for k, v in ss.forms.items() if not profile.forms[k].get("after_registration")}, apply_date, ss.timeline_spec)
            ss.submitted_id = rec["id"]
            st.rerun()

# ---------- 4. 周知チラシ ----------
elif step.startswith("4."):
    st.subheader("4. 周知チラシ（地域へのお知らせ）")
    st.caption("参考様式に沿って本文を作ります。捕獲の前に配布・掲示するものです。")
    a = ss.anchors
    period = ""
    if a.get("trap"):
        period = f"{a['trap'].isoformat()} 〜"
    period = st.text_input("捕獲予定期間（空欄なら記入欄のまま）", value=period)
    if st.button("作成", type="primary"):
        with st.spinner("作成しています…"):
            ss.flyer = flyer.generate_flyer(llm, profile, ss.colony, period)
            ss.notified = True
    if ss.flyer:
        st.text_area("本文", ss.flyer, height=520)
        st.download_button("テキストをダウンロード", data=ss.flyer.encode("utf-8"), file_name="osirase.txt", mime="text/plain")

# ---------- 5. 日程表 ----------
elif step.startswith("5."):
    st.subheader("5. 日程表")
    st.caption("工程の並びと期限は一次資料から抽出します。日付の計算はコード側です。資料に日数の記載が無いものは「記載なし」と出します。")
    if ss.timeline_spec is None:
        if st.button("要綱から工程と期限を抽出", type="primary"):
            with st.spinner("一次資料を読んでいます…"):
                ss.timeline_spec = schedule.extract_timeline_spec(llm, profile)
            st.rerun()
    else:
        spec = ss.timeline_spec
        st.markdown("**基準日**（決まっているものだけ入力。登録日を入れると報告と更新の期限が出ます）")
        a = ss.anchors
        c = st.columns(6)
        labels = [("apply", "申請日"), ("register", "登録日"), ("notify", "周知日"), ("trap", "捕獲日"), ("surgery", "持込日"), ("return_", "リターン日")]
        for (k, lab), col in zip(labels, c):
            with col:
                on = st.checkbox(lab, value=a.get(k) is not None, key=f"on_{k}")
                if on:
                    a[k] = st.date_input(lab, value=a.get(k) or a.get("apply") or dt.date.today(), key=f"d_{k}", label_visibility="collapsed")
                else:
                    a[k] = None
        if ss.submitted_id and (rec := registry.get(ss.submitted_id)) and rec.get("registered_date"):
            a["register"] = dt.date.fromisoformat(rec["registered_date"])
            st.caption(f"登録日は台帳（{ss.submitted_id}）の値を使っています。")
        anchors = schedule.Anchors(**a)
        rows = schedule.build_timeline(spec, anchors)
        st.markdown("---")
        w = spec.get("application_window")
        if w:
            st.markdown("**最短日程（受付期間から計算）**")
            ready = st.date_input("準備完了日（申請書類が揃う日）", value=dt.date.today(), key="ready_date")
            e = schedule.earliest_schedule(spec, ready)
            c1, c2, c3 = st.columns(3)
            c1.metric("最短の申請日", e["apply"].isoformat())
            c2.metric("チケット有効期間", f"{e['valid_from']} 〜 {e['valid_until']}", help=f"準備完了から {e['wait_days']} 日")
            c3.metric("この受付を逃すと", f"+{e['delay_days']} 日", help=f"次の申請 {e['missed_apply']}、有効 {e['missed_valid_from']} から")
            st.caption(f"受付：毎月{w['from_day']}日〜{w['to_day'] or '末'}日、交付は申請月の{w['ticket_month_offset']}か月後の分、{w['valid_months']}か月有効"
                       + (f"、上限{w['max_tickets']}枚" if w.get("max_tickets") else "") + "。出典：「" + w["source_quote"] + "」")
            st.caption("規則で決まる待ちはツールでは消せません。消せるのは、受付を逃す・報告を落とす・書類の不備で戻される、の3つです。")
        else:
            st.caption("この制度には受付期間の定め（毎月◯日〜、翌月分など）がありません。審査・現地調査の日数は自治体の裁量で、資料に記載がありません。")
        st.markdown("---")
        for r in rows:
            d = r.date.strftime("%Y-%m-%d（%a）") if r.date else "—"
            docs = "、".join(r.documents) if r.documents else ""
            st.markdown(
                f"**{d}**　{r.label}　<small>［{r.who}］{r.date_note}</small>  \n"
                f"<small>{r.description}{('　提出物：' + docs) if docs else ''}</small>",
                unsafe_allow_html=True,
            )
        st.info(f"更新：{spec['renewal_note']}  \n終了時：{spec['termination_note']}")
        if spec.get("other_deadlines"):
            st.markdown("**条件付きで発生する提出物**")
            for d_ in spec["other_deadlines"]:
                st.markdown(f"- {d_['label']}：{d_['condition']}　<small>「{d_['source_quote']}」</small>", unsafe_allow_html=True)
        with st.expander("抽出元の引用"):
            for s in spec["steps"]:
                st.markdown(f"- {s['label']}：「{s['source_quote']}」")

# ---------- 6. 自治体面 ----------
elif step.startswith("6."):
    st.subheader("6. 自治体面：登録コロニー一覧")
    st.caption(f"{profile.office}の職員が見る画面。市民面で提出された申請・報告がそのまま載ります。状態は、要綱から抽出した期限ルールと報告履歴から計算しています。「期限超過」のうち届出が無いものは、この一覧が無ければ理由が残らない地域です。")
    rows = registry.rows()
    counts = {}
    for r in rows:
        counts[r["状態"]] = counts.get(r["状態"], 0) + 1
    st.markdown("　".join(f"**{k}** {v}件" for k, v in counts.items()))
    st.dataframe(rows, use_container_width=True, hide_index=True)
    ids = [r["ID"] for r in rows]
    default = ids.index(ss.submitted_id) if ss.submitted_id in ids else 0
    cid = st.selectbox("詳細を見るコロニー", ids, index=default)
    rec = registry.get(cid)
    d = registry.deadlines(rec)
    st.markdown(f"#### {rec['id']}　{rec['ward']}{rec.get('town', '')}　{rec['location']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("状態", d["status"])
    c2.metric("頭数／手術済", f"{rec['cat_count']}／{rec['ear_tipped_count']}")
    if rec.get("kind") == "ticket":
        c3.metric("報告期限（有効月末）", d["next_report_due"].isoformat() if d["next_report_due"] else "—", help=f"有効期間 {rec.get('ticket_valid_from')} 〜")
        c4.metric("チケット枚数", rec.get("tickets") or "—")
    else:
        c3.metric("次回報告期限", d["next_report_due"].isoformat() if d["next_report_due"] else "—",
                  help=f"基準日（登録日と同月日）{d['next_report_base']} から{(rec.get('rules') or {}).get('annual_report_window_days')}日以内" if d["next_report_base"] else None)
        c4.metric("更新満了日", d["renewal_due"].isoformat() if d["renewal_due"] else "—",
                  help=f"更新申請は {d['renewal_open']} から満了日まで" if d["renewal_open"] else None)
    if d["status"] == "更新待ち":
        st.warning(f"更新申請の受付期間です（{d['renewal_open']} 〜 {d['renewal_due']}）。第2号様式と実施計画書の提出が必要です。")
    if not rec.get("registered_date"):
        is_ticket = rec.get("kind") == "ticket"
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
            for fld in doc["fields"]:
                st.markdown(f"- {fld['label']}：{fld['value'] or '（空欄）'}".replace("\n", " "))
    with tab2:
        if not rec.get("reports"):
            st.caption("報告はまだありません。")
        for rp in sorted(rec.get("reports", []), key=lambda r: r["date"], reverse=True):
            st.markdown(f"**{rp['date']}**　頭数 {rp['cat_count']}／手術済 {rp['ear_tipped_count']}／この1年の手術 {rp.get('surgeries', '—')}頭  \n{rp['summary']}")

# ---------- 7. 年次報告 ----------
elif step.startswith("7."):
    rep_label = next((s["label"] for s in (ss.timeline_spec or {}).get("steps", []) if s["key"] == "annual_report"), "報告")
    st.subheader(f"7. 報告（市民面）：{rep_label}")
    st.caption("会話で内容を集めて報告書にし、提出すると自治体面の状態が変わります。")
    registered = [r for r in registry.all() if r.get("registered_date")]
    if not registered:
        st.warning("登録（交付）済みのコロニーがありません。「6. 自治体面」で登録してください。")
        st.stop()
    ids = [r["id"] for r in registered]
    default = ids.index(ss.submitted_id) if ss.submitted_id in ids else 0
    cid = st.selectbox("報告するコロニー", ids, index=default, format_func=lambda i: f"{i}　{registry.get(i)['ward']}{registry.get(i).get('town', '')} {registry.get(i)['location']}")
    if ss.get("report_cid") != cid:
        ss.report_cid = cid
        ss.report_chat, ss.report_draft, ss.report_done = [], None, False
    rec = registry.get(cid)
    d = registry.deadlines(rec)
    st.markdown(f"状態：**{d['status']}**　次回報告：基準日 {d['next_report_base'] or '—'} ／ 期限 {d['next_report_due'] or '—'}")
    if ss.report_done:
        st.success("提出しました。「6. 自治体面」で状態を確認できます。")
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
        st.markdown(f"**報告書の内容**　現在管理する猫 {rp['cat_count']}頭／うち手術済 {rp['ear_tipped_count']}頭／手術 {rp['surgeries']}頭  \n{rp['summary']}")
        if st.button("医療衛生センターへ提出", type="primary"):
            today = dt.date.today()
            registry.submit_report(cid, {"date": today.isoformat(), **rp})
            ss.report_docx = report.build_report_docx(profile, rec, rp, today, ss.timeline_spec)
            ss.report_done = True
            st.rerun()
    user_text = st.chat_input("回答を入力", disabled=ss.report_draft is not None)
    if user_text:
        ss.report_chat.append({"role": "user", "content": user_text})
        hist = [m for m in ss.report_chat if m["role"] in ("user", "assistant")]
        first_user = next(i for i, m in enumerate(hist) if m["role"] == "user")
        with st.spinner("整理しています…"):
            try:
                out = report.report_turn(llm, profile, rec, hist[first_user:])
            except Exception as e:
                st.error(f"LLM 呼び出しに失敗しました: {e}")
                st.stop()
        ss.report_chat.append({"role": "assistant", "content": out["reply"]})
        if out["complete"] and out["report"]:
            ss.report_draft = out["report"]
        st.rerun()
