import os
import sys
import threading
import webbrowser

BASE_DIR = getattr(sys, "_M_EIPASS", os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if os.path.isdir(BACKEND_DIR) and BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
elif BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.main import app


def configure_static_frontend():
    candidates = [
        os.path.join(BASE_DIR, "frontend_dist"),
        os.path.join(BASE_DIR, "frontend", "dist"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist"),
    ]
    for dist_dir in candidates:
        index_html = os.path.join(dist_dir, "index.html")
        if os.path.isfile(index_html):
            assets_dir = os.path.join(dist_dir, "assets")
            if os.path.isdir(assets_dir):
                app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

            @app.get("/")
            def serve_index():
                return FileResponse(index_html)

            app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")
            break


configure_static_frontend()


def main():
    host = "127.0.0.1"
    port = int(os.environ.get("PORT", "8000"))
    proto = "http"
    threading.Timer(1.5, lambda: webbrowser.open(f"{proto}://{host}:{port}")).start()
    uvicorn.run(app, host=host, port=port, log_config=None)


if __name__ == "__main__":
    main()
