from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from backend.app.main import create_app


def main() -> None:
    state_file = os.getenv("SINAV_OKUMA_STATE_FILE", "").strip()
    host = os.getenv("SINAV_OKUMA_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.getenv("SINAV_OKUMA_PORT", "8140").strip() or "8140")
    app = create_app(Path(state_file) if state_file else None)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()