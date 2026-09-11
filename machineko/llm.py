"""LLM API の薄いラッパー。

- 資料束（自治体プロファイルの corpus）は system に置き、prompt caching を効かせる。
- Anthropic: 構造化出力は output_config.format（JSON Schema）で受ける。
- OpenAI互換（DeepSeek / OpenAI / Ollama 等）: JSONモード＋スキーマをプロンプトに書いて受ける。
  切り替えは環境変数 MACHINEKO_PROVIDER（anthropic / openai）。未指定ならキーの有無で判定。
- 認証情報が無いときはモック（machineko.mock）に切り替える。デモUIが必ず動くようにするため。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

def _provider() -> str | None:
    """anthropic / openai / None（モック）。"""
    if os.environ.get("MACHINEKO_MOCK") == "1":
        return None
    p = os.environ.get("MACHINEKO_PROVIDER")
    if p in ("anthropic", "openai"):
        return p
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return "anthropic"
    if os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        return "openai"
    # `ant auth login` のプロファイル
    if (Path.home() / ".config" / "anthropic").exists():
        return "anthropic"
    return None


def _default_model(provider: str | None) -> str:
    if os.environ.get("MACHINEKO_MODEL"):
        return os.environ["MACHINEKO_MODEL"]
    if provider == "openai":
        return "deepseek-chat" if os.environ.get("DEEPSEEK_API_KEY") else "gpt-4.1"
    return "claude-sonnet-5"


DEFAULT_MODEL = _default_model(_provider())


def _log(task: str, model: str, text: str) -> None:
    """MACHINEKO_LOG=1 のとき、各呼び出しの生応答を data/llm_log.jsonl に追記する（検証用）。"""
    if os.environ.get("MACHINEKO_LOG") != "1":
        return
    import datetime as _dt

    path = Path(__file__).resolve().parent.parent / "data" / "llm_log.jsonl"
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": _dt.datetime.now().isoformat(timespec="seconds"), "task": task, "model": model, "response": text}, ensure_ascii=False) + "\n")


def _has_credentials() -> bool:
    return _provider() is not None


class LLM:
    def __init__(self, model: str = DEFAULT_MODEL, mock: bool | None = None):
        self.model = model
        self.provider = _provider()
        self.mock = (self.provider is None) if mock is None else mock
        self._client = None
        if not self.mock:
            if self.provider == "openai":
                import openai

                # DeepSeek は OpenAI 互換。DEEPSEEK_API_KEY があればそれを使い、base_url を DeepSeek に向ける。
                base_url = os.environ.get("OPENAI_BASE_URL")
                api_key = os.environ.get("OPENAI_API_KEY")
                if os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
                    api_key = os.environ["DEEPSEEK_API_KEY"]
                    base_url = base_url or "https://api.deepseek.com"
                self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
            else:
                import anthropic

                self._client = anthropic.Anthropic()

    @property
    def mode_label(self) -> str:
        if self.mock:
            return "モック応答（APIキー未設定）"
        if self.provider == "openai":
            host = os.environ.get("OPENAI_BASE_URL") or ("api.deepseek.com" if os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("OPENAI_API_KEY") else "api.openai.com")
            return f"OpenAI互換API（{self.model} @ {host}）"
        return f"Anthropic API（{self.model}）"

    # ---- OpenAI 互換 ----
    def _oa_system(self, system: str, corpus: str | None, schema: dict | None) -> str:
        parts = [system]
        if corpus:
            parts.append("以下は自治体の一次資料です。規則はここからのみ抽出し、資料に無いことは断定しないでください。\n\n" + corpus)
        if schema is not None:
            parts.append("出力は次の JSON Schema に厳密に従う JSON オブジェクトのみを返してください。前置き・説明・コードフェンスは不要です。\n\n" + json.dumps(schema, ensure_ascii=False))
        return "\n\n".join(parts)

    def _oa_call(self, system: str, messages: list[dict], schema: dict | None) -> str:
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=8000,
            messages=[{"role": "system", "content": system}, *messages],
        )
        if schema is not None:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self._client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        if choice.finish_reason == "content_filter":
            raise RuntimeError("モデルが応答を拒否しました")
        return choice.message.content or ""

    @staticmethod
    def _parse_json(text: str) -> dict:
        s = text.strip()
        if s.startswith("```"):
            s = s.strip("`")
            s = s[s.find("{"):]
        start, end = s.find("{"), s.rfind("}")
        return json.loads(s[start:end + 1] if start >= 0 else s)

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
        if self.provider == "openai":
            raw = self._oa_call(self._oa_system(system, corpus, schema), [{"role": "user", "content": user}], schema)
            _log(task, self.model, raw)
            return self._parse_json(raw)
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
        _log(task, self.model, text)
        return json.loads(text)

    def text(self, task: str, system: str, user: str, corpus: str | None = None, ctx: dict | None = None) -> str:
        if self.mock:
            from . import mock

            return mock.dispatch(task, ctx or {})
        if self.provider == "openai":
            raw = self._oa_call(self._oa_system(system, corpus, None), [{"role": "user", "content": user}], None)
            _log(task, self.model, raw)
            return raw
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=self._system_blocks(system, corpus),
            messages=[{"role": "user", "content": user}],
        )
        if resp.stop_reason == "refusal":
            raise RuntimeError("モデルが応答を拒否しました")
        out = "".join(b.text for b in resp.content if b.type == "text")
        _log(task, self.model, out)
        return out

    def chat_json(self, task: str, system: str, messages: list[dict], schema: dict, corpus: str | None = None, ctx: dict | None = None) -> dict:
        """会話履歴を渡して、構造化された1ターン分の応答を受ける（聞き取り用）。"""
        if self.mock:
            from . import mock

            return mock.dispatch(task, ctx or {})
        if self.provider == "openai":
            raw = self._oa_call(self._oa_system(system, corpus, schema), messages, schema)
            _log(task, self.model, raw)
            return self._parse_json(raw)
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
        _log(task, self.model, text)
        return json.loads(text)
