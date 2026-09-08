import threading
import webbrowser

from app import create_app

app = create_app()

HOST = "127.0.0.1"
PORT = 5000


def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False,
    )
