import threading
import webbrowser
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.scheduled_tasks import check_expirations, accrue_leave_balances

from app import create_app
HOST = "127.0.0.1"
PORT = 5000

app = create_app()


scheduler = BackgroundScheduler(timezone="America/Chicago")

scheduler.add_job(
    func=check_expirations,
    trigger="cron",
    hour=8,
    minute=0,
    id="expiration_checker",
    replace_existing=True
)
scheduler.add_job(
    func=accrue_leave_balances,
    trigger="cron",
    day=1,
    hour=8,
    minute=0,
    id="leave_accrual",
    replace_existing=True
)

scheduler.start()

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
