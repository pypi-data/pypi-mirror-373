import os
import types
import builtins
import json
import pytest

from telelog.core import env_config, _truncate, _escapeMarkdownV2, TelegramConfigError


def test_env_config_missing_raises(monkeypatch):
    for k in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_IDS"]:
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(TelegramConfigError):
        env_config()


def test_truncate_limit():
    text = "x" * 5000
    out = _truncate(text)
    assert len(out) == 4096
    assert out.endswith("...")


def test_markdown_escape():
    s = "_ * [ ] ( ) ~ ` > # + - = | { } . !"
    out = _escapeMarkdownV2(s)
    # Todos devem estar escapados
    for ch in s.split():
        assert f"\\{ch}" in out
