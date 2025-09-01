from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://api.telegram.org/bot{token}/sendMessage"
MAX_MESSAGE_LEN = 4096


class TelegramConfigError(Exception):
    """Erro de configuração de credenciais e parâmetros do Telegram."""


class TelelogSendError(Exception):
    """Erro ao enviar mensagem ao Telegram após tentativas e backoff."""


@dataclass
class TeleConfig:
    """Configurações para envio ao Telegram.

    Atributos:
    - botToken: Token do bot.
    - chatIds: Lista de chat IDs (inteiros em string, incluindo IDs negativos para grupos).
    - parseMode: None, "MarkdownV2" ou "HTML".
    - timeout: Timeout de requisição em segundos.
    - retries: Número de tentativas totais (inclui a primeira).
    - backoffBaseMs: Base do backoff exponencial em milissegundos.
    - jitter: Fator de jitter (0-1) aplicado ao backoff.
    """

    botToken: str
    chatIds: List[str]
    parseMode: Optional[str] = None
    timeout: float = 5.0
    retries: int = 3
    backoffBaseMs: int = 500
    jitter: float = 0.2


def _loadDotenvIntoEnv(envPath: str = ".env") -> None:
    """Carrega pares chave=valor de um arquivo .env simples no ambiente, se existir."""
    if not os.path.exists(envPath):
        return
    try:
        with open(envPath, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Não sobrescreve se já existir no ambiente
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Não falha se .env estiver inválido; segue com variáveis atuais
        pass


def env_config() -> TeleConfig:
    """Lê configuração do ambiente (.env e variáveis de ambiente).

    Returns:
        TeleConfig
    Raises:
        TelegramConfigError: se faltar TELEGRAM_BOT_TOKEN e CHAT_ID(S).
    """
    _loadDotenvIntoEnv()

    botToken = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chatIdsRaw = os.environ.get("TELEGRAM_CHAT_IDS") or os.environ.get("TELEGRAM_CHAT_ID", "")
    parseMode = os.environ.get("TELEGRAM_PARSE_MODE")

    if not botToken or not chatIdsRaw:
        raise TelegramConfigError(
            "Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID(S). Consulte o README."
        )

    chatIds: List[str] = []
    for part in str(chatIdsRaw).replace(";", ",").replace(" ", ",").split(","):
        p = part.strip()
        if p:
            chatIds.append(p)
    if not chatIds:
        raise TelegramConfigError(
            "Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID(S). Consulte o README."
        )

    if parseMode:
        parseMode = parseMode.strip()
        if parseMode not in ("MarkdownV2", "HTML"):
            # Ignora valor inválido e usa texto puro
            parseMode = None

    return TeleConfig(
        botToken=botToken,
        chatIds=chatIds,
        parseMode=parseMode,
    )


def _escapeMarkdownV2(text: str) -> str:
    """Escapa caracteres reservados do MarkdownV2 do Telegram."""
    specials = r"_ * [ ] ( ) ~ ` > # + - = | { } . !".split()
    escaped = []
    for ch in text:
        if ch in specials:
            escaped.append("\\" + ch)
        else:
            escaped.append(ch)
    return "".join(escaped)


def _escapeHtml(text: str) -> str:
    """Escapa caracteres especiais em HTML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _truncate(text: str, maxLen: int = MAX_MESSAGE_LEN) -> str:
    """Trunca texto ao limite, anexando '...' quando necessário."""
    if len(text) <= maxLen:
        return text
    cut = maxLen - 3
    out = text[:cut] + "..."
    # Evita barra invertida no final (MarkdownV2)
    if out.endswith("\\"):
        out = out[:-1]
    return out


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def _calcBackoff(attempt: int, baseMs: int, jitter: float) -> float:
    # backoff exponencial: baseMs * (2 ** (attempt-1)) com jitter +-20%
    ms = baseMs * (2 ** max(0, attempt - 1))
    jitterFactor = 1.0 + (jitter * (2 * (os.urandom(1)[0] / 255.0 - 0.5)))
    return (ms * jitterFactor) / 1000.0


def _postJson(url: str, payload: dict, timeout: float) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def send_telegram(text: str, cfg: Optional[TeleConfig] = None, **kwargs: Any) -> List[dict]:
    """Envia mensagem de texto ao Telegram para 1+ chat IDs.

    Args:
        text: Conteúdo textual da mensagem.
        cfg: Configuração opcional; se omitido, usa env_config().
    Returns:
        Lista de respostas (uma por chatId).
    Raises:
        TelegramConfigError | TelelogSendError
    """
    if cfg is None:
        cfg = env_config()

    if not isinstance(text, str):
        text = str(text)

    sendText = text
    if cfg.parseMode == "MarkdownV2":
        sendText = _escapeMarkdownV2(sendText)
    elif cfg.parseMode == "HTML":
        sendText = _escapeHtml(sendText)

    sendText = _truncate(sendText, MAX_MESSAGE_LEN)

    url = API_URL.format(token=cfg.botToken)

    results: List[dict] = []
    for chatId in cfg.chatIds:
        attempt = 1
        lastErr: Optional[Exception] = None
        succeeded = False
        while attempt <= max(1, cfg.retries):
            payload = {
                "chat_id": chatId,
                "text": sendText,
            }
            if cfg.parseMode:
                payload["parse_mode"] = cfg.parseMode

            try:
                res = _postJson(url, payload, timeout=cfg.timeout)
                results.append(res)
                succeeded = True
                break
            except HTTPError as he:  # type: ignore
                status = getattr(he, "code", None)
                body = he.read().decode("utf-8") if hasattr(he, "read") else ""
                retryAfter: Optional[float] = None
                try:
                    parsed = json.loads(body or "{}")
                    params = parsed.get("parameters", {}) if isinstance(parsed, dict) else {}
                    ra = params.get("retry_after")
                    if isinstance(ra, (int, float)):
                        retryAfter = float(ra)
                except Exception:
                    pass

                # 429 respeita retry_after; 5xx/408 usam backoff
                if status == 429 and retryAfter is not None:
                    _sleep(retryAfter)
                    attempt += 1
                    lastErr = he
                    continue
                elif status in {408, 500, 502, 503, 504}:
                    backoff = _calcBackoff(attempt, cfg.backoffBaseMs, cfg.jitter)
                    _sleep(backoff)
                    attempt += 1
                    lastErr = he
                    continue
                else:
                    lastErr = he
                    break
            except URLError as ue:  # inclui timeouts
                backoff = _calcBackoff(attempt, cfg.backoffBaseMs, cfg.jitter)
                _sleep(backoff)
                attempt += 1
                lastErr = ue
                continue
            except Exception as e:
                lastErr = e
                break

        if not succeeded:
            raise TelelogSendError(f"Falha ao enviar para chat_id={chatId}: {lastErr}")

    return results
