import logging
import os
import signal
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from app.bot import handler
from app.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def shutdown(signum, frame):
    logger.info("Shutting down...")
    if handler.mcp_client is not None:
        try:
            handler.mcp_client.__exit__(None, None, None)
        except Exception:
            pass
    sys.exit(0)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass  # suppress request logs


def _start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Health server listening on port {port}")


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    _start_health_server()

    platform = settings.platform.lower()
    logger.info(f"Starting FootballBot on {platform}...")

    if platform == "discord":
        from app.bot.discord import run_discord_bot

        run_discord_bot()
    else:
        from app.bot.telegram import create_telegram_application

        app = create_telegram_application()
        logger.info("Telegram bot is running. Press Ctrl+C to stop.")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
