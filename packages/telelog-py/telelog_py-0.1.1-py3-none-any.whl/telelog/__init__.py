"""telelog-py pacote.

APIs públicas:
- send_telegram(text, cfg=None, **kwargs) -> list[dict]
- env_config() -> TeleConfig
- TelegramLogHandler
"""

from .core import TeleConfig, env_config, send_telegram, TelegramConfigError, TelelogSendError
from .cli import main as cli_main
from .logging_handler import TelegramLogHandler

__all__ = [
    "TeleConfig",
    "env_config",
    "send_telegram",
    "TelegramLogHandler",
    "TelegramConfigError",
    "TelelogSendError",
    "cli_main",
]

__version__ = "0.1.1"
