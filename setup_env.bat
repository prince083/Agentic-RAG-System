@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Setup complete. Run 'python -m app.main' or 'uvicorn app.main:app --reload' to start.
pause
