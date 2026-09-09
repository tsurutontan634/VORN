"""まちねこ事務局AI — Streamlit UI。

左のメニューが完成の定義（HANDOFF §6-3）の 1→6 に対応する。
永続化はしない。全部 st.session_state に置く。
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import streamlit as st

from machineko import documents, flyer, intake, rules, schedule
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


@st.cache_resource
def get_llm() -> LLM:
    return LLM()


@st.cache_resource
def get_profile(mid: str):
    return load_profile(mid)


llm = get_llm()
profile = get_profile(ss.municipality)


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
        ss.municipality = mid
        st.rerun()
    step = st.radio(
        "工程",
        ["1. 聞き取り", "2. 要綱照合", "3. 書類出力", "4. 周知チラシ", "5. 日程表", "6. リマインド"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"LLM：{llm.mode_label}")
    avail = [s.file for s in profile.sources if s.available]
    missing = profile.missing_sources()
    st.caption(f"読み込んだ一次資料：{len(avail)}件")
    if missing:
        with st.expander(f"未配置の資料 {len(missing)}件"):
            for s in missing:
                st.markdown(f"- `{s.file}` — {s.role}")
            st.caption(f"`municipality/{profile.id}/sources/` に置くと自動で読み込みます。")
    st.divider()
    if st.button("デモ用のコロニー情報を読み込む", use_container_width=True):
        ss.colony = Colony.from_dict(json.loads((Path("demo") / "sample_colony.json").read_text(encoding="utf-8")))
        ss.intake_complete = True
        ss.chat = [{"role": "assistant", "content": "デモ用のコロニー情報を読み込みました。内容は右側に表示しています。"}]
        reset_derived()
        st.rerun()
    if st.button("すべてリセット", use_container_width=True):
        for k in list(ss.keys()):
            del ss[k]
        st.rerun()

# ---------- header ----------
st.markdown(f"#### {profile.name}　{profile.program_name}")
st.caption("対象：町内会等への説明と同意が済んだ後 〜 完了報告まで。捕獲の手順・自治会への説得・里親探し・子猫の育て方は扱いません。")


def colony_panel():
    st.markdown("**コロニー情報**")
    for line in ss.colony.summary_lines():
        st.markdown(line)
    with st.expander("JSON"):
        st.code(ss.colony.to_json(), language="json")


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
        st.markdown("**基準日**（決まっているものだけ入力。登録日を入れると年次報告と更新の期限が出ます）")
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
        anchors = schedule.Anchors(**a)
        rows = schedule.build_timeline(spec, anchors)
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
        with st.expander("抽出元の引用"):
            for s in spec["steps"]:
                st.markdown(f"- {s['label']}：「{s['source_quote']}」")

# ---------- 6. リマインド ----------
elif step.startswith("6."):
    st.subheader("6. リマインド一覧")
    if ss.timeline_spec is None:
        st.warning("先に「5. 日程表」で工程と期限を抽出してください。")
    else:
        anchors = schedule.Anchors(**ss.anchors)
        rows = schedule.build_timeline(ss.timeline_spec, anchors)
        rem = schedule.build_reminders(ss.timeline_spec, rows)
        if not anchors.register:
            st.info("登録日が未入力です。「5. 日程表」で登録日を入れると期限が確定します。")
        for r in rem:
            if r["date"]:
                st.markdown(f"**{r['date']}**（あと {r['days_left']} 日）　{r['label']}　<small>{r['note']}／{r['lead_days']}日前に通知</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"**条件付き**　{r['label']}　<small>{r['note']}</small>", unsafe_allow_html=True)
        st.caption("通知の送信先（メール等）は本プロトタイプでは未実装です。一覧の生成までを対象にしています。")
