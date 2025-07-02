@echo off
cd %~dp0
git init
git add .
git commit -m "Initial commit from pro bot"
git remote add origin https://github.com/IBMaxin/eth_scalp_pro_bot.git
git branch -M main
git push -u origin main
pause
