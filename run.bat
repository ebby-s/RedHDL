@echo off

echo [INFO] Finding OrangeCrab revision and USB busid.

wsl -e echo
set "devln=none"
set "devid=none"
set "devrv=none"
for /F "delims=" %%a in  ('usbipd wsl list ^| find "OrangeCrab"') do set "devln=%%a"
for /F "tokens=1" %%a in ("%devln%") do set "devid=%%a"
for /F "usebackq tokens=*" %%a in (`powershell -command "$str = '%devln%'; $regex = '(r\d+\.\d+)'; if ($str -match $regex) { $matches[1] }"`) do (
    set "devrv=%%a"
)

echo %devln% | findstr /C:"Not" > nul

if "%devid%"=="none" (
    echo [INFO] No OrangeCrab device found, continuing without DFU.
) else (
    if %errorlevel% equ 0 (
        echo [INFO] Found OrangeCrab Rev. %devrv% at busID %devid%, attaching to WSL.
        usbipd wsl attach --busid %devid%
    ) else (
        echo [INFO] OrangeCrab Rev. %devrv% at busID %devid% already attached.
    )
)


echo [INFO] Capturing Minecraft world.

python main.py

wsl ./build.sh
