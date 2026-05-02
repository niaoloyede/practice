#!/usr/bin/env python3
"""
Serve the static SVG demo with the stdlib only (no pip dependencies).

  cd svg-python-demo
  python3 server.py

Then open http://127.0.0.1:8765/ — index embeds animation.svg via <object>.
Direct SVG: http://127.0.0.1:8765/animation.svg
"""

from __future__ import annotations

import http.server
import socketserver
from pathlib import Path

PORT = 8765
ROOT = Path(__file__).resolve().parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        # quieter logs
        return


def main() -> None:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving {ROOT}")
        print(f"  http://127.0.0.1:{PORT}/")
        print(f"  http://127.0.0.1:{PORT}/animation.svg")
        print("Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
