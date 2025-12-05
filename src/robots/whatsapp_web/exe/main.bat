@echo off
cd /d "C:\automatizaciones_sem"
call env\Scripts\activate
python -m src.robots.whatsapp_web.app
pause