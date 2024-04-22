@echo off
echo Press Y to continue or N to cancel the installation...
set /p UserInput=Continue with installation? (Y/N):
if /I "%UserInput%" neq "Y" goto end

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment and installing dependencies...
cmd /c ".\venv\Scripts\activate && pip install -v -r requirements.txt && echo Installation completed."

:end
pause
