"""デモ7手順を自動で回してスクリーンショットを撮る。

使い方（リポジトリ直下で）:
    pip install playwright
    playwright install chromium
    set/export DEEPSEEK_API_KEY=...   # 無ければモックで回る
    python demo/shoot.py

出力: build/shots_real/*.png と data/llm_log.jsonl（各API呼び出しの生応答）。
Streamlit はこのスクリプトが起動・終了する。台帳はデモ初期状態に戻してから回す。
"""
from __future__ import annotations

import asyncio
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "shots_real"
PORT = int(os.environ.get("SHOOT_PORT", "8599"))
URL = f"http://localhost:{PORT}"


def _wait_port(timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with socket.socket() as s:
            s.settimeout(1)
            if s.connect_ex(("127.0.0.1", PORT)) == 0:
                return True
        time.sleep(0.5)
    return False


async def run():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        pg = await b.new_page(viewport={"width": 1440, "height": 1700}, device_scale_factor=1.5)
        SB = "[data-testid='stSidebar']"

        async def idle(min_ms=600, timeout=240_000):
            """Streamlit の実行中インジケータが消えるまで待つ（実APIは1回10〜60秒かかる）。"""
            await pg.wait_for_timeout(min_ms)
            try:
                await pg.wait_for_selector("[data-testid='stStatusWidget']", state="hidden", timeout=timeout)
            except Exception:
                pass
            await pg.wait_for_timeout(700)

        async def step(label):
            await pg.locator(SB + " label", has_text=label).click(); await idle()

        async def mode(label):
            await pg.locator(SB + " label", has_text=label).click(); await idle()

        async def say(t):
            await pg.fill("textarea[data-testid='stChatInputTextArea']", t)
            await pg.keyboard.press("Enter"); await idle(1200)

        async def click(name, first=True):
            loc = pg.get_by_role("button", name=name)
            await (loc.first if first else loc).click(); await idle(1200)

        async def shot(name, full=True):
            await pg.evaluate("document.querySelectorAll('section,div').forEach(e=>{if(e.scrollHeight>e.clientHeight) e.scrollTop=0})")
            await pg.wait_for_timeout(400)
            await pg.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
            print("shot", name, flush=True)

        await pg.goto(URL, wait_until="networkidle"); await idle(2500)
        await shot("k1_start", False)
        await say("左京区北白川、公園西の駐車場。11頭くらい、耳カットは2匹。3人でやります")
        await say("餌場はうちの玄関脇1か所。18時に2人で")
        await shot("k1_chat")
        await say("庭にトイレ2つ、朝7時に掃除。苦情は私に")
        await say("北白川町内会の高橋さんに8/23説明、同意あり。回覧板で周知")
        await say("山田花子・佐藤一郎・鈴木良子")
        await shot("k1_intake")
        await step("2. 要綱照合")
        await click("① 要綱から規則を抽出")
        await click("② コロニー情報を照合")
        await shot("k2_rules")
        await step("5. 日程表")
        await click("要綱から工程と期限を抽出")
        await shot("k5_timeline_pre")
        await step("3. 書類出力")
        for i in range(2):
            tabs = await pg.get_by_role("tab").all()
            await tabs[i].click(); await idle(500)
            await click("作成")
        tabs = await pg.get_by_role("tab").all(); await tabs[0].click(); await idle(500)
        await shot("k3_docs")
        await pg.locator("button", has_text="へ提出").first.click(); await idle(1200)
        await shot("k3_submitted")
        await mode("自治体面（窓口）")
        await shot("k6_city_pending")
        await click("登録する")
        await shot("k6_city_registered")
        await mode("市民面（活動者）")
        await shot("k0_next", False)
        await step("4. 周知チラシ")
        await click("作成")
        await shot("k4_flyer")
        await step("5. 日程表")
        await shot("k5_timeline")
        await step("6. 報告")
        await say("今は12頭、全部手術済み")
        await say("10頭手術した。新しく1匹来た。苦情なし")
        await shot("k7_report")
        await pg.locator("button", has_text="へ提出").first.click(); await idle(1200)
        await shot("k7_done")
        await mode("自治体面（窓口）")
        await shot("k6_city_after")
        # ---- 高島市 ----
        await mode("市民面（活動者）")
        await pg.locator(SB + " [data-testid='stSelectbox']").first.click(); await pg.wait_for_timeout(800)
        await pg.get_by_role("option", name="高島市").click(); await idle(1500)
        await say("今津町、民宿の裏。6頭、手術済みなし、子猫3匹")
        await say("民宿の裏口で朝6時と夕方5時。病院は隣の市、車で40分")
        await say("個人です。森綾子、高島市今津町在住")
        await shot("t1_intake")
        await step("2. 要綱照合")
        await click("① 要綱から規則を抽出")
        await click("② コロニー情報を照合")
        await shot("t2_rules")
        await step("5. 日程表")
        await click("要綱から工程と期限を抽出")
        await shot("t5_timeline")
        await mode("自治体面（窓口）")
        await shot("t6_city")
        await b.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.png"):
        f.unlink()
    data = ROOT / "data"
    if data.exists():
        shutil.rmtree(data)
    env = dict(os.environ, MACHINEKO_LOG="1")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"), "--server.headless", "true",
         "--server.port", str(PORT), "--browser.gatherUsageStats", "false"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    try:
        if not _wait_port():
            raise SystemExit("Streamlit が起動しませんでした")
        asyncio.run(run())
        print(f"\n完了: {OUT} と {data / 'llm_log.jsonl'} を送ってください。")
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
