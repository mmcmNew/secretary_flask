@echo off
echo ������� Y ��� ����������� ��� N ��� ������ ���������...
set /p UserInput=���������� ���������? (Y/N):
if /I "%UserInput%" neq "Y" goto :end

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
echo ��������� ���������.

:end
pause