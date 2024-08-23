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
## Upload your own payloads by changing the payload.dd file with yours, but make sure it is still called payload.dd
## The pico_rubber_ducky.py script has to be executed every time you want a different payload to be uploaded.
![pico](https://github.com/user-attachments/assets/c7acd0e2-e798-4744-90bb-ee101897b69a)
