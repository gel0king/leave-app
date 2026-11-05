import threading
import webbrowser
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.scheduled_tasks import check_expirations, driver_policy_renewal

from app import create_app
HOST = "127.0.0.1"
PORT = 5000

app = create_app()


scheduler = BackgroundScheduler(timezone="America/Chicago")

def run_with_app_context(func):
    with app.app_context():
        func()

scheduler.add_job(
    func=run_with_app_context,
    args=[check_expirations],
    trigger="cron",
    hour=10,
    minute=41,
    id="expiration_checker",
    replace_existing=True,
)

scheduler.add_job(
    func=run_with_app_context,
    args=[driver_policy_renewal],
    trigger="cron",
    day=1,
    hour=8,
    minute=0,
    id="leave_accrual",
    replace_existing=True,
)

scheduler.start()

def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()

    try:
        app.run(
            host=HOST,
            port=PORT,
            debug=False,
            use_reloader=True,
        )
    finally:
        scheduler.shutdown(wait=True)