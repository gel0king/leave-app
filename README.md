# Leave Ledger

Small local app to track accrued leave. It runs locally on your computer using SQLite as a database.

## What it does

- Tracks employees, leave types (Sick, and Annual Leave) and all accrual, usage, or manual adjustment.
- Calculates balances automatically
- Keep sa full history of every entry, who it was for, and when.
- Data in `leave_data.db`, SQLite file.

## Set up

You will need Python installed

1. Open terminal / cmd in this folder.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Runing it

```
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. Leave the terminal open while you use it. To stop the app close the therminal.
