@echo off
cd /d "c:\Users\jucx\Downloads\aero4j\novo_projeto_aero_final"
git add backend/server.py
git commit -m "fix: auto-detect available Gemini model with fallback list"
git push origin main
pause
