@echo off
cd /d "%~dp0"
echo El Takibi Studio - Yerel sanal ortam kurulumu
python -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 goto error
echo Kurulum tamamlandi. Baslat.bat ile uygulamayi acabilirsiniz.
pause
exit /b 0
:error
echo Kurulum tamamlanamadi. Yukaridaki hata mesajini kontrol edin.
pause
exit /b 1
