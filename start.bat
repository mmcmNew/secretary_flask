@echo echo_on
call .\.venv\Scripts\activate
set FLASK_APP=app.py
set FLASK_ENV=development
echo Starting the Flask application...
flask run
echo Flask application has stopped.
pause
