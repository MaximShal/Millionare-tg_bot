@echo off

call C:\Users\Maksim\PycharmProjects\pythonProject\venv\Scripts\activate

cd %~dp0

set TOKEN=5751249144:AAH8AnNtkUkAZ9aHlFDaOCPKp9w3veBy6ow

python telegram_bot.py

pause