@echo off
echo Нажмите Y для продолжения или N для отмены установки...
set /p UserInput=Продолжить установку? (Y/N):
if /I "%UserInput%" neq "Y" goto :end

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
echo Установка завершена.

:end
pause