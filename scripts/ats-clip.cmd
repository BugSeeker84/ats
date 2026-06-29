@echo off
REM One-key ATS launcher (Windows): read the JD from the clipboard, auto-pick the best
REM candidate, generate the resume + cover letter, open the PDF, and show a notification.
REM Bind this to a hotkey with scripts\setup-hotkey.ps1.
cd /d "%~dp0.."
".venv\Scripts\python.exe" -m ats generate --clipboard --yes --open --notify %*