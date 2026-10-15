@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d %~dp0
echo [微信收款监控] 启动中... (关闭本窗口即停止)
python -m monitor.worker
pause