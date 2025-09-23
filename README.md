# arduino_camera
arduino pro nicla vision

## 1. Install OpenMV tools

Download & install OpenMV IDE
 (Windows/Linux/Mac).

Connect your Nicla Vision via USB.

Open the OpenMV and connect the camera by clicking the outlet icon (Ctrl E)

It will prompt you to update firmware → install OpenMV firmware on the Nicla Vision.

Test by running an example. File → Examples → OpenMV → Image Processing.

## 2. Multiple files

If you want to divide the code in multiple files, you will get include errors.

To surpass this, you will need to move the files you want to include into the nicla vision USB drive, found in the file explorer. Changing these files is a bit more difficult, but it works.