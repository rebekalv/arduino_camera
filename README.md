# arduino_camera
arduino pro nicla vision

## 1. Install OpenMV tools

Download & install OpenMV IDE
 (Windows/Linux/Mac).

Connect your Nicla Vision via USB.

Open the OpenMV and click connect (Ctrl E, the outlet icon)

It will prompt you to update firmware → install OpenMV firmware on the Nicla Vision.

Test by running an example (File → Examples → OpenMV → Image Processing).

## 2. Develop in VSCode instead of IDE

Install Python extension in VSCode.

Install mpremote (for uploading scripts to microcontrollers):

python -m pip install mpremote


In VSCode:

Write your .py scripts.

Use mpremote to upload to Nicla Vision:

mpremote connect COM4 fs cp main.py :

(replace com4 with your nicla visions com port)