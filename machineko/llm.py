"""Anthropic API の薄いラッパー。

- 資料束（自治体プロファイルの corpus）は system に置き、prompt caching を効かせる。
- 構造化出力は output_config.format（JSON Schema）で受ける。
- 認証情報が無いときはモック（machineko.mock）に切り替える。デモUIが必ず動くようにするため。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_MODEL = os.environ.get("MACHINEKO_MODEL", "claude-sonnet-5")


def _has_credentials() -> bool:
    if os.environ.get("MACHINEKO_MOCK") == "1":
        return False
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    # `ant auth login` のプロファイル
    return (Path.home() / ".config" / "anthropic").exists()


class LLM:
    def __init__(self, model: str = DEFAULT_MODEL, mock: bool | None = None):
        self.model = model
        self.mock = (not _has_credentials()) if mock is None else mock
        self._client = None
        if not self.mock:
            import anthropic

            self._client = anthropic.Anthropic()

    @property
    def mode_label(self) -> str:
        return "モック応答（APIキー未設定）" if self.mock else f"Anthropic API（{self.model}）"

    # ---- 低レベル ----
    def _system_blocks(self, system: str, corpus: str | None) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = [{"type": "text", "text": system}]
        if corpus:
            blocks.append({"type": "text", "text": "以下は自治体の一次資料です。規則はここからのみ抽出し、資料に無いことは断定しないでください。\n\n" + corpus,
                           "cache_control": {"type": "ephemeral"}})
        return blocks

    def json(self, task: str, system: str, user: str, schema: dict, corpus: str | None = None, ctx: dict | None = None) -> dict:
        if self.mock:
            from . import mock

            return mock.dispatch(task, ctx or {})
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=self._system_blocks(system, corpus),
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
        if resp.stop_reason == "refusal":
            raise RuntimeError("モデルが応答を拒否しました")
        text = next(b.text for b in resp.content if b.type == "text")
        return json.loads(text)

    def text(self, task: str, system: str, user: str, corpus: str | None = None, ctx: dict | None = None) -> str:
        if self.mock:
            from . import mock

            return mock.dispatch(task, ctx or {})
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=self._system_blocks(system, corpus),
            messages=[{"role": "user", "content": user}],
        )
        if resp.stop_reason == "refusal":
            raise RuntimeError("モデルが応答を拒否しました")
        return "".join(b.text for b in resp.content if b.type == "text")

    def chat_json(self, task: str, system: str, messages: list[dict], schema: dict, corpus: str | None = None, ctx: dict | None = None) -> dict:
        """会話履歴を渡して、構造化された1ターン分の応答を受ける（聞き取り用）。"""
        if self.mock:
            from . import mock

            return mock.dispatch(task, ctx or {})
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=self._system_blocks(system, corpus),
            messages=messages,
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
        if resp.stop_reason == "refusal":
            raise RuntimeError("モデルが応答を拒否しました")
        text = next(b.text for b in resp.content if b.type == "text")
        return json.loads(text)
