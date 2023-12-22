@echo off
echo "Hello from tmbinc, j005u and Bin4ry"
echo "Please do not leak this!"
echo "+-+-+-+-+-+-+-+-+-+-+-+-"
echo "Connect Mavic 3 powered off, then press any key and only then power it on!"
echo "+-+-+-+-+-+-+-+-+-+-+-+-"

pause
.\bin\libusbex.exe .\bin\e2-bootarea.img.pro.enc
.\bin\fastboot.exe flash bootloader .\image\e2\e2-bootarea-new.img
.\bin\fastboot.exe flash bootloader2 .\image\e2\e2-bootarea-new.img
.\bin\fastboot.exe flash normal .\image\e2\e2-normal-new.img
.\bin\fastboot.exe flash normal_2 .\image\e2\e2-normal-new.img
.\bin\fastboot.exe flash system .\image\e2\e2-system-new.img
.\bin\fastboot.exe flash system_2 .\image\e2\e2-system-new.img
.\bin\fastboot.exe flash vendor .\image\e2\e2-vendor-new.img
.\bin\fastboot.exe flash vendor_2 .\image\e2\e2-vendor-new.img
.\bin\fastboot.exe erase env
.\bin\fastboot.exe erase blackbox
.\bin\fastboot.exe reboot

timeout /T 45 /NOBREAK
python .\dji-firmware-tools\pop_shell_e2.py
if %ERRORLEVEL% NEQ 0 (
	echo "Exploit failed, please check and start over"
 	pause
 	exit
 )
timeout /T 10 /NOBREAK

.\bin\adb.exe wait-for-device
.\bin\adb.exe shell "mkdir -p /blackbox/e1e_image/"

.\bin\adb.exe push .\bin\e1e-bootarea.img.pro.enc /blackbox/e1e_image/bootarea.img.pro.enc
.\bin\adb.exe push .\bin\e1e-bootarea.img.pro.enc.reboot /blackbox/e1e_image/bootarea.img.pro.enc.reboot

.\bin\adb.exe push .\image\e1e\bootarea.img /blackbox/e1e_image/bootarea.img
.\bin\adb.exe push .\image\e1e\normal.img /blackbox/e1e_image/normal.img
.\bin\adb.exe push .\image\e1e\normal-adb.img /blackbox/e1e_image/normal-adb.img
.\bin\adb.exe push .\image\e1e\system.img /blackbox/e1e_image/system.img
.\bin\adb.exe push .\image\e1e\vendor.img /blackbox/e1e_image/vendor.img
.\bin\adb.exe push .\image\e1e\rtos.img /blackbox/e1e_image/rtos.img
.\bin\adb.exe push .\image\e1e\env.img /blackbox/e1e_image/env.img
.\bin\adb.exe push .\image\e1e\wm260.cfg.sig /blackbox/e1e_image/wm260.cfg.sig


rem REBOOT SLAVE CHIP
.\bin\adb.exe shell "echo 1 > /sys/class/gpio/unexport"
.\bin\adb.exe shell "echo 1 > /sys/class/gpio/export"
.\bin\adb.exe shell "echo 50 > /sys/class/gpio/unexport"
.\bin\adb.exe shell "echo 50 > /sys/class/gpio/export"

.\bin\adb.exe shell "echo out > /sys/class/gpio/gpio50/direction"
.\bin\adb.exe shell "echo 1 > /sys/class/gpio/gpio50/value"

.\bin\adb.exe shell "echo out > /sys/class/gpio/gpio1/direction"
.\bin\adb.exe shell "echo 0 > /sys/class/gpio/gpio1/value"
.\bin\adb.exe shell "echo 1 > /sys/class/gpio/gpio1/value"
REM REBOOT END

.\bin\adb.exe shell "brload /blackbox/e1e_image/bootarea.img.pro.enc.reboot"
.\bin\adb.exe shell "brload /blackbox/e1e_image/bootarea.img.pro.enc"

.\bin\adb.exe shell "fastboot flash bootloader  /blackbox/e1e_image/bootarea.img"
.\bin\adb.exe shell "fastboot flash bootloader2 /blackbox/e1e_image/bootarea.img"
.\bin\adb.exe shell "fastboot flash normal  /blackbox/e1e_image/normal-adb.img"
.\bin\adb.exe shell "fastboot flash normal_2 /blackbox/e1e_image/normal-adb.img"
.\bin\adb.exe shell "fastboot flash system  /blackbox/e1e_image/system.img"
.\bin\adb.exe shell "fastboot flash system_2 /blackbox/e1e_image/system.img"
.\bin\adb.exe shell "fastboot flash vendor  /blackbox/e1e_image/vendor.img"
.\bin\adb.exe shell "fastboot flash vendor_2 /blackbox/e1e_image/vendor.img"
.\bin\adb.exe shell "fastboot flash rtos /blackbox/e1e_image/rtos.img"
.\bin\adb.exe shell "fastboot flash rtos_2 /blackbox/e1e_image/rtos.img"
.\bin\adb.exe shell "fastboot flash env /blackbox/e1e_image/env.img"

rem REBOOT e1e
.\bin\adb.exe shell "echo 0 > /sys/class/gpio/gpio1/value && sleep 1"
.\bin\adb.exe shell "echo 1 > /sys/class/gpio/gpio1/value"

timeout /T 10 /NOBREAK

.\bin\adb.exe shell "echo 0 > /sys/class/gpio/gpio1/value && sleep 1"
.\bin\adb.exe shell "echo 1 > /sys/class/gpio/gpio1/value"

rem PUSH e1e .cfg.sig
.\bin\adb.exe shell "adb wait-for-device"
.\bin\adb.exe shell "adb push /blackbox/e1e_image/wm260.cfg.sig /data/upgrade/wm260/wm260.cfg.sig"
.\bin\adb.exe shell "adb shell sync"

rem REBOOT e1e one final time and flash stock normal.img
.\bin\adb.exe shell "adb shell reboot"
.\bin\adb.exe shell "brload /blackbox/e1e_image/bootarea.img.pro.enc"

.\bin\adb.exe shell "fastboot flash normal  /blackbox/e1e_image/normal.img"
.\bin\adb.exe shell "fastboot flash normal_2  /blackbox/e1e_image/normal.img"
.\bin\adb.exe shell "fastboot reboot-bootloader"

.\bin\adb.exe shell "echo 0 > /sys/class/gpio/gpio50/value"
.\bin\adb.exe shell "rm -rf /blackbox/e1e_image"
rem .\bin\adb.exe shell "reboot"


echo "Done, please reboot the drone manually to load patched FC"
pause