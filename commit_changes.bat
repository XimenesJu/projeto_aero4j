@echo off
cd /d "c:\Users\jucx\Downloads\aero4j\novo_projeto_aero_final"
git add backend/server.py backend/requirements.txt frontend/src/App.js
git commit -m "feat: implement full Brazil and complete dataset loading from CSV URLs"
git push origin main
echo.
echo Commit completed!
pause
