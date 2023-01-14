@echo off

call C:\Users\Maksim\PycharmProjects\pythonProject\venv\Scripts\activate

cd %~dp0

set TOKEN=

python millionare.py

pause