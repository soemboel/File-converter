@echo off
REM Build aplikasi standalone (.exe) - hasil: dist\KonverterSerbaguna.exe
REM Pakai virtualenv bersih supaya ukuran exe kecil.
if not exist .venv python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt pyinstaller
.venv\Scripts\python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name KonverterSerbaguna ^
  --icon favicon\favicon.ico ^
  --paths script ^
  --add-data "favicon;favicon" ^
  --collect-all tkinterdnd2 ^
  --collect-all svglib ^
  --collect-all pdf2docx ^
  --collect-submodules reportlab ^
  script\app.py
echo.
echo Selesai. Taruh ffmpeg.exe di sebelah dist\KonverterSerbaguna.exe untuk fitur Audio/Video.
