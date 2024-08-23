#!/usr/bin/env python3
import subprocess
import time
from colorama import Fore

def get_disks_and_partitions():
    result = subprocess.run(['lsblk', '-o', 'NAME,TYPE,SIZE,MOUNTPOINT'], capture_output=True, text=True)
    output = result.stdout.splitlines()
    disks = {}
    current_disk = None
    for line in output[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        name, type_, *rest = parts
        name = name.lstrip('└─├─')
        if type_ == 'disk':
            current_disk = name
            disks[current_disk] = []
        elif type_ == 'part' and current_disk:
            disks[current_disk].append(name)
    return disks

def size_to_int(size):
    """Convert size to integer value in megabytes."""
    size = size.strip()
    if size.endswith('G'):
        return int(float(size[:-1]) * 1024)  # Convert GB to MB
    elif size.endswith('M'):
        return int(size[:-1])
    else:
        return 0

def find_pico_disk(disks):
    pico_disk = None
    min_size = float('inf')
    for disk, partitions in disks.items():
        if len(partitions) == 0:
            continue
        size_result = subprocess.run(['lsblk', '-o', 'SIZE', f'/dev/{disk}'], capture_output=True, text=True)
        size = size_result.stdout.splitlines()[1].strip()
        size_value = size_to_int(size)
        if size_value < min_size:
            min_size = size_value
            pico_disk = disk
    return pico_disk

def select_and_mount_disk():
    disks = get_disks_and_partitions()
    if disks:
        selected_disk = find_pico_disk(disks)
        if selected_disk:
            #print(f"Selected disk: {selected_disk}")
            mount_point = '/mnt/pico'
            subprocess.run(f'sudo mount /dev/{selected_disk}1 {mount_point}', shell=True)
            return selected_disk, mount_point
    return None, None

def mv_to(file_path, target_path, disconnect_state):
    subprocess.run(f'cp -r {file_path} {target_path}', shell=True)
    if disconnect_state == 0:
        print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + str(file_path) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.RESET)
    elif disconnect_state == 1:
        print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + str(file_path) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.YELLOW + ' (Pico will temporarily disconnect)' + Fore.RESET)



if __name__ == "__main__":
    selected_disk, mount_point = select_and_mount_disk()
    if selected_disk and mount_point:
        print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'pico-ducky' + Fore.LIGHTGREEN_EX + ' Repository ...' + Fore.RESET)
        pico_ducky_folder = 'pico-ducky'
        subprocess.run('git clone --quiet https://github.com/dbisu/pico-ducky.git', shell=True)

        print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'flash_nuke.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
        nuke_old_data_folder = 'flash_nuke'
        subprocess.run('curl -s -L -o flash_nuke.zip https://forum.micropython.org/download/file.php?id=1388&sid=506b47f59603becf1d3bb0ca98a95189', shell=True)
        time.sleep(5)
        print(Fore.GREEN + 'Unziping ' + Fore.LIGHTBLUE_EX + 'flash_nuke.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
        subprocess.run('unzip -qq flash_nuke.zip', shell=True)

        print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
        subprocess.run('curl -s -O https://downloads.circuitpython.org/bin/raspberry_pi_pico_w/en_US/adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2', shell=True)

        print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-bundle-9.x-mpy-20240822.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
        subprocess.run('curl -s -L -O https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20240822/adafruit-circuitpython-bundle-9.x-mpy-20240822.zip', shell=True)
        
        print(Fore.GREEN + 'Unziping ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-bundle-9.x-mpy-20240822.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
        subprocess.run('unzip -qq adafruit-circuitpython-bundle-9.x-mpy-20240822.zip', shell=True)
        circuit_python_folder = 'adafruit-circuitpython-bundle-9.x-mpy-20240822'

        mv_to('flash_nuke.uf2', mount_point, 1)  # delete old data
        time.sleep(20)
        
        # Re-select and re-mount disk after sleep
        selected_disk, mount_point = select_and_mount_disk()
        if selected_disk and mount_point:
            mv_to('adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2', mount_point, 1)  # update data
            time.sleep(45)

            # Re-select and re-mount disk again
            selected_disk, mount_point = select_and_mount_disk()
            if selected_disk and mount_point:
                mv_to(f'{circuit_python_folder}/lib/adafruit_hid', f'{mount_point}/lib', 0)
                mv_to(f'{circuit_python_folder}/lib/adafruit_debouncer.mpy', f'{mount_point}/lib', 0)
                mv_to(f'{circuit_python_folder}/lib/adafruit_ticks.mpy', f'{mount_point}/lib', 0)
                mv_to(f'{circuit_python_folder}/lib/asyncio', f'{mount_point}/lib', 0)
                mv_to(f'{circuit_python_folder}/lib/adafruit_wsgi', f'{mount_point}/lib', 0)

                mv_to(f'{pico_ducky_folder}/boot.py', mount_point, 0)
                mv_to(f'{pico_ducky_folder}/duckyinpython.py', mount_point, 0)
                mv_to(f'{pico_ducky_folder}/code.py', mount_point, 0)
                mv_to(f'{pico_ducky_folder}/webapp.py', mount_point, 0)
                mv_to(f'{pico_ducky_folder}/wsgiserver.py', mount_point, 0)

                mv_to('payload.dd', mount_point, 0)

                # Optionally unmount the disk after operations
                subprocess.run(f'sudo umount {mount_point}', shell=True)
        
        subprocess.run('rm -rf adafruit-circuitpython-bundle-9.x-mpy-20240822',shell=True)
        subprocess.run('rm -rf pico-ducky',shell=True)
        subprocess.run('rm adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2',shell=True)
        subprocess.run('rm flash_nuke.zip',shell=True)
        subprocess.run('rm adafruit-circuitpython-bundle-9.x-mpy-20240822.zip',shell=True)
        try:
            subprocess.run('rm flash_nuke.uf2',shell=True)
            subprocess.run('rm -rf d',shell=True)
        except:
            print('')
        
