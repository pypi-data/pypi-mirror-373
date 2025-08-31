import logging
import sys
from typing import Optional

from .core import TeleConfig, send_telegram, env_config, TelelogSendError, TelegramConfigError


class TelegramLogHandler(logging.Handler):
    """Handler de logging que envia registros ao Telegram.

    Não bloqueia a aplicação em caso de erro: falhas são emitidas em stderr.
    """

    def __init__(self, cfg: Optional[TeleConfig] = None, level: int = logging.NOTSET) -> None:
        super().__init__(level=level)
        self.cfg = cfg

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            cfg = self.cfg or env_config()
            send_telegram(msg, cfg)
        except (TelegramConfigError, TelelogSendError) as e:
            print(f"[telelog] erro ao enviar log: {e}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"[telelog] erro inesperado: {e}", file=sys.stderr)
