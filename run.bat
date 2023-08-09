@echo off

echo [INFO] Capturing Minecraft world.

python main.py


echo [INFO] Finding OrangeCrab revision and USB busid.

@REM Find devid (Device ID) and devrv (Device Revision).
set "devln=none"
set "devid=none"
set "devrv=none"
for /F "delims=" %%a in  ('usbipd wsl list ^| find "OrangeCrab"') do set "devln=%%a"
for /F "tokens=1" %%a in ("%devln%") do set "devid=%%a"
for /F "usebackq tokens=*" %%a in (`powershell -command "$str = '%devln%'; $regex = '(r\d+\.\d+)'; if ($str -match $regex) { $matches[1] }"`) do (
    set "devrv=%%a"
)

@REM Start WSL before moving USB device from Windows to WSL.
wsl -e echo

if "%devid%"=="none" (
    echo [INFO] No OrangeCrab device found, continuing without DFU.
) else (
    echo %devln% | findstr /C:"Not" > nul

    if %errorlevel% equ 0 (
        echo [INFO] Found OrangeCrab Rev. %devrv% at busID %devid%, attaching to WSL.
        usbipd wsl attach --busid %devid%
    ) else (
        echo [INFO] OrangeCrab Rev. %devrv% at busID %devid% already attached.
    )
)

@REM Generate bitstream and flash to device from WSL.
wsl ./build.sh
