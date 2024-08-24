#!/usr/bin/env python3
import subprocess
import time
import os.path
from colorama import Fore
import argparse

parser = argparse.ArgumentParser(description='Process some arguments.')
parser.add_argument('-clean', action='store_true', help='Delete all downloaded data at the end')
args = parser.parse_args()

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

def cp_file_to(file_path, target_path, disconnect_state):
    subprocess.run(f'cp -r {file_path} {target_path}', shell=True)
    if disconnect_state == 0:
        print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + str(file_path) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
    elif disconnect_state == 1:
        print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + str(file_path) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.YELLOW + ' (Pico will temporarily disconnect)' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)

def cp_folder_to(file_path, target_path, disconnect_state):
    subprocess.run(f'cp -r {file_path} {target_path}', shell=True)
    if disconnect_state == 0:
        print(Fore.LIGHTGREEN_EX + 'Folder ' + Fore.LIGHTBLUE_EX + str(file_path) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
    elif disconnect_state == 1:
        print(Fore.LIGHTGREEN_EX + 'Folder ' + Fore.LIGHTBLUE_EX + str(file_path) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.YELLOW + ' (Pico will temporarily disconnect)' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)

def check_file_exist(path):
    return os.path.isfile(path)

def check_dir_exist(path):
    return os.path.isdir(path)

def cp_payload_to(file_path, target_path, disconnect_state):
    subprocess.run(f'cp -r {file_path} {target_path}', shell=True)
    if disconnect_state == 0:
        payload_name = file_path.replace('payloads/','')
        print(Fore.LIGHTGREEN_EX + 'Payload ' + Fore.LIGHTBLUE_EX + str(payload_name) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
    elif disconnect_state == 1:
        payload_name = file_path.replace('payloads/','')
        print(Fore.LIGHTGREEN_EX + 'Payload ' + Fore.LIGHTBLUE_EX + str(payload_name) + Fore.LIGHTGREEN_EX + ' copied to ' + Fore.LIGHTBLUE_EX + str(target_path) + Fore.YELLOW + ' (Pico will temporarily disconnect)' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)

def get_file_names(folder_path):
    # List to store file names
    file_names = []

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Check if it's a file (not a directory)
        if os.path.isfile(os.path.join(folder_path, file_name)):
            # Add file name to the list
            file_names.append(file_name)

    return file_names

if __name__ == "__main__":
    selected_disk, mount_point = select_and_mount_disk()
    if selected_disk and mount_point:

        if check_dir_exist('pico-ducky') == True:
            print(Fore.LIGHTGREEN_EX + 'Folder ' + Fore.LIGHTBLUE_EX + 'pico-ducky' + Fore.LIGHTGREEN_EX + ' Already Downloaded ...' + Fore.RESET)
            pico_ducky_folder = 'pico-ducky'
        else:
            print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'pico-ducky' + Fore.LIGHTGREEN_EX + ' Repository ...' + Fore.RESET)
            subprocess.run('git clone --quiet https://github.com/dbisu/pico-ducky.git', shell=True)
            pico_ducky_folder = 'pico-ducky'

        if check_file_exist('flash_nuke.uf2') == True:
            print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + 'flash_nuke.uf2' + Fore.LIGHTGREEN_EX + ' Already Downloaded ...' + Fore.RESET)
            nuke_old_data_folder = 'flash_nuke'
        elif check_file_exist('flash_nuke.zip') == True:
            print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + 'flash_nuke.zip' + Fore.LIGHTGREEN_EX + ' Already Downloaded ...' + Fore.RESET)
            print(Fore.GREEN + 'Unziping ' + Fore.LIGHTBLUE_EX + 'flash_nuke.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
            subprocess.run('unzip -qq flash_nuke.zip', shell=True)
            time.sleep(5)
            nuke_old_data_folder = 'flash_nuke'
        else:
            print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'flash_nuke.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
            subprocess.run('curl -s -L -o flash_nuke.zip https://forum.micropython.org/download/file.php?id=1388&sid=506b47f59603becf1d3bb0ca98a95189', shell=True)
            time.sleep(5)
            print(Fore.GREEN + 'Unziping ' + Fore.LIGHTBLUE_EX + 'flash_nuke.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
            subprocess.run('unzip -qq flash_nuke.zip', shell=True)
            nuke_old_data_folder = 'flash_nuke'


        if check_file_exist('adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2') == True:
            print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2' + Fore.LIGHTGREEN_EX + ' Already Downloaded ...' + Fore.RESET)
        else:
            print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
            subprocess.run('curl -s -O https://downloads.circuitpython.org/bin/raspberry_pi_pico_w/en_US/adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2', shell=True)


        if check_dir_exist('adafruit-circuitpython-bundle-9.x-mpy-20240822') == True:
            print(Fore.LIGHTGREEN_EX + 'Folder ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-bundle-9.x-mpy-20240822' + Fore.LIGHTGREEN_EX + ' Already Downloaded ...' + Fore.RESET)
            circuit_python_folder = 'adafruit-circuitpython-bundle-9.x-mpy-20240822'
        elif check_file_exist('adafruit-circuitpython-bundle-9.x-mpy-20240822.zip') == True:
            print(Fore.LIGHTGREEN_EX + 'File ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-bundle-9.x-mpy-20240822.zip' + Fore.LIGHTGREEN_EX + ' Already Downloaded ...' + Fore.RESET)
            print(Fore.GREEN + 'Unziping ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-bundle-9.x-mpy-20240822.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
            subprocess.run('unzip -qq adafruit-circuitpython-bundle-9.x-mpy-20240822.zip > /dev/null 2>&1', shell=True)
            circuit_python_folder = 'adafruit-circuitpython-bundle-9.x-mpy-20240822'
        else:
            print(Fore.LIGHTGREEN_EX + 'Downloading ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-bundle-9.x-mpy-20240822.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
            subprocess.run('curl -s -L -O https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20240822/adafruit-circuitpython-bundle-9.x-mpy-20240822.zip', shell=True)
            time.sleep(5)
            print(Fore.GREEN + 'Unziping ' + Fore.LIGHTBLUE_EX + 'adafruit-circuitpython-bundle-9.x-mpy-20240822.zip' + Fore.LIGHTGREEN_EX + ' ...' + Fore.RESET)
            subprocess.run('unzip -qq adafruit-circuitpython-bundle-9.x-mpy-20240822.zip', shell=True)
            circuit_python_folder = 'adafruit-circuitpython-bundle-9.x-mpy-20240822'

        print('\n')
        cp_file_to('flash_nuke.uf2', mount_point, 1)  # delete old data
        time.sleep(20)
        
        # Re-select and re-mount disk after sleep
        selected_disk, mount_point = select_and_mount_disk()
        if selected_disk and mount_point:
            cp_file_to('adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.1.2.uf2', mount_point, 1)  # update data
            time.sleep(45)

            # Re-select and re-mount disk again
            selected_disk, mount_point = select_and_mount_disk()
            if selected_disk and mount_point:
                cp_folder_to(f'{circuit_python_folder}/lib/adafruit_hid', f'{mount_point}/lib', 0)
                cp_file_to(f'{circuit_python_folder}/lib/adafruit_debouncer.mpy', f'{mount_point}/lib', 0)
                cp_file_to(f'{circuit_python_folder}/lib/adafruit_ticks.mpy', f'{mount_point}/lib', 0)
                cp_folder_to(f'{circuit_python_folder}/lib/asyncio', f'{mount_point}/lib', 0)
                cp_folder_to(f'{circuit_python_folder}/lib/adafruit_wsgi', f'{mount_point}/lib', 0)

                cp_file_to(f'{pico_ducky_folder}/boot.py', mount_point, 0)
                cp_file_to(f'{pico_ducky_folder}/duckyinpython.py', mount_point, 0)
                cp_file_to(f'{pico_ducky_folder}/code.py', mount_point, 0)
                cp_file_to(f'{pico_ducky_folder}/webapp.py', mount_point, 0)
                cp_file_to(f'{pico_ducky_folder}/wsgiserver.py', mount_point, 0)

                print('\n')
                cp_payload_to('payloads/payload.dd', mount_point, 0)

                # Optionally unmount the disk after operations
                subprocess.run(f'sudo umount {mount_point}', shell=True)
        
                if args.clean:
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
        
