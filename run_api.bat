@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
echo [收款API服务] http://127.0.0.1:5000 启动中...
python -m app.main
pause