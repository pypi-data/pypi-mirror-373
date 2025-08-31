import argparse
import sys

from .core import env_config, send_telegram, TelegramConfigError, TelelogSendError


def main() -> None:
    """CLI: telelog "mensagem".

    Saídas:
    - Código 0: sucesso
    - Código 1: falha de envio
    - Código 2: uso incorreto ou configuração ausente
    """
    parser = argparse.ArgumentParser(prog="telelog", description="Enviar mensagem ao Telegram")
    parser.add_argument("mensagem", nargs="*", help="Mensagem a enviar")
    args = parser.parse_args()

    if not args.mensagem:
        print("Uso: telelog \"mensagem\"", file=sys.stderr)
        raise SystemExit(2)

    text = " ".join(args.mensagem)

    try:
        cfg = env_config()
    except TelegramConfigError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2)

    try:
        send_telegram(text, cfg)
        raise SystemExit(0)
    except TelelogSendError as e:
        print(f"Falha ao enviar: {e}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as e:  # noqa: BLE001
        print(f"Erro inesperado: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
