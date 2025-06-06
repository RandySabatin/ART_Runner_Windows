CALL C:\virtualpython\PYTHON3.7.9-X32\Scripts\activate.bat

pyinstaller --log-level=DEBUG --clean main.spec

del /Q .\dist\ART_Runner.exe
rename .\dist\main.exe ART_Runner.exe

pause