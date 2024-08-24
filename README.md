# Make a cheap clone of Hak5's Rubber Ducky
## Fully automated script to setup the pico and install a payload
Automated script based on: [pico-ducky](https://github.com/dbisu/pico-ducky) 
## Instructions
1) Insert the Pico to the pc while holding the BOOTSEL button
2) After 10 seconds run the script
```
python pico_rubber_ducky.py
```
3) When the installation is completed, remove the pico from the pc, cause it will reboot and execute the payload we just uploaded.

## The current payload is launching fullscreen rick roll on youtube 
## Upload your own payloads by changing the payload.dd file inside folder /payloads with yours, but make sure it is still called payload.dd
![download_all_pico_normal](https://github.com/user-attachments/assets/2312b81a-9191-4ad5-b6f7-8aebd8bb8950)

## If files already exist it will skip the download process
![already_downloaded](https://github.com/user-attachments/assets/b57d003f-85ba-434b-a923-0cf3ff47eb36)

# Multiple Payloads
## Add the option to select between mutiple payloads on the go
This is a way to select payloads on the go using 8 DIP switches for 8 binary positions to decode in decimal system and then select the corresponding payload eg. 00010010 = 18 = payload18.dd
```
python pico_rubber_ducky_multiple.py
```
## Make sure to add all the payloads in the payloads folder and name then accordingly starting from (payload.dd, payload1.dd, payload2.dd)
The maximum number is 11111111 = 256 = payload256.dd
#
![download_all_pico_multiple](https://github.com/user-attachments/assets/8a0cec18-1e14-4238-8d01-035e5d8b4c6d)

# Circuit
![pico_circuit](https://github.com/user-attachments/assets/3ca9337b-508a-4cbb-8c13-8cc416436774)

# -clean
## You can run both script with the '-clean' argument to delete all downloaded data at the end of the script.
```
python pico_rubber_ducky.py -clean 
```
```
python pico_rubber_ducky_multiple.py -clean
```
