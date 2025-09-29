# TTK8 - Object Detection with an Arduino Nicla Vision Camera

This project uses the OpenMV firmware to implement object detection on the Arduino Nicla Vision camera. It uses the integrated Time of Flight distance sensor (ToF) to measure the distance to the nearest obstacle. The system combines blob detection and wifi streaming to identify and track objects in real-time.

![System Overview](images/system_overview.jpg)
_Complete system setup showing Nicla Vision camera in operation_

## Prerequisites

### 1. Install OpenMV IDE

Download & install OpenMV IDE (Windows/Linux/Mac).

1. Connect your Nicla Vision via USB
2. Open the OpenMV IDE and connect the camera by clicking the outlet icon (Ctrl+E)
3. It will prompt you to update firmware → install OpenMV firmware on the Nicla Vision
4. Test by running an example: File → Examples → OpenMV → Image Processing

### 2. Hardware Requirements

- Arduino Pro Nicla Vision
- USB cable for programming and power
- WiFi network with a 2.4GHz bandwidth for streaming (optional)

![Hardware Setup](images/hardware_setup.jpg)
_Arduino Pro Nicla Vision with USB connection_

## Features

- **Real-time blob detection**: Detects dark/bright objects, standing out from the background
- **Distance measurement**: Uses integrated ToF sensor for distance readings
- **WiFi streaming**: Optional live video streaming to web browser
- **Adaptive filtering**: Ignores objects that are too small or too large
- **Target tracking**: Prioritizes objects in the center of the field of view

![Object Detection Demo](images/detection_demo.jpg)
_Example of object detection with distance measurement overlay_

## Configuration

### Camera Settings

- **Format**: Grayscale (optimized for detection)
- **Resolution**: QVGA (320x240)
- **Frame rate**: Optimized for real-time processing

### Detection Parameters

```python
THRESHOLD_TYPE = "dark"      # "dark" or "bright" objects
OFFSET = 30                  # Threshold offset around mean brightness
min_area = 300              # Minimum blob area (pixels)
min_pixels = 300            # Minimum blob pixel count
max_fraction = 0.95         # Maximum blob size (95% of image)
MIN_VALID_DISTANCE = 40     # Minimum valid ToF reading (mm)
```

### WiFi Configuration

To enable WiFi streaming, modify these parameters in `ttk8.py`:

```python
ENABLE_WIFI_STREAMING = True # Or False to disable wifi streaming
WIFI_NAME = "your_network_name"
KEY = "your_password"
```

![OpenMV IDE Setup](images/openmv_ide_setup.jpg)
_OpenMV IDE interface with ttk8.py loaded and connected to Nicla Vision_

## Usage
Without Wifi Streaming
1. Open `ttk8.py` in OpenMV IDE and set 'ENABLE_WIFI_STREAMING' to False.
2. Connect your Nicla Vision to the computer with a USB cable. In the OpenMV IDE click connect (outlet icon) and hit play - it will automatically start object detection

With wifi streaming
1. Open `ttk8.py` in OpenMV IDE and set `ENABLE_WIFI_STREAMING` to True.
2. Configure the WiFi parameters (`WIFI_NAME` and `KEY`) as described in the [WiFi Configuration](#wifi-configuration) section. Make sure your WiFi supports 2.4 GHz band.
3. Connect your Nicla Vision to the computer with a USB cable. In the OpenMV IDE click connect (outlet icon) and hit play - it will tell you to open a browser and access the stream at http://192.168.1.30:8080/
3. When the stream works, upload the code to the Nicla Vision by selecting Tools->Save open script to OpenMV Cam
4. Disconnect the camera from the computer and connect it to a power source
   - The camera will automatically connect to the specified network
   - Open a browser and navigate to the stream http://192.168.1.30:8080/
   - View the live stream with obstacle detection

![WiFi Stream Example](images/wifi_stream_browser.jpg)
_Live video stream in web browser showing real-time object detection_

## Algorithm Overview

1. **Image Capture**: Captures grayscale images at QVGA resolution
2. **Adaptive Thresholding**: Calculates dynamic threshold based on image brightness
3. **Blob Detection**: Identifies objects using configurable size filters
4. **Distance Measurement**: Reads ToF sensor for precise distance data
5. **Target Selection**: Prioritizes objects in the center of the field of view
6. **Visualization**: Draws detection boxes and distance information
7. **Streaming**: Optionally streams processed frames via WiFi

![Algorithm Flowchart](images/algorithm_flowchart.jpg)
_Visual representation of the detection algorithm workflow_

## Results and Examples

### Detection Performance

![Dark Object Detection](images/dark_object_detection.jpg)
_Dark object detection with distance measurement_

![Bright Object Detection](images/bright_object_detection.jpg)
_Bright object detection example_

![Multiple Objects](images/multiple_objects_detection.jpg)
_Handling multiple objects in the field of view_

### Different Lighting Conditions

![Low Light Performance](images/low_light_detection.jpg)
_Object detection in low light conditions_

![Bright Light Performance](images/bright_light_detection.jpg)
_Object detection under bright lighting_

### Distance Measurement Accuracy

![Distance Accuracy Test](images/distance_accuracy_test.jpg)
_Distance measurement accuracy demonstration_

![Close Range Detection](images/close_range_detection.jpg)
_Close range object detection (minimum 40mm)_

![Far Range Detection](images/far_range_detection.jpg)
_Long range object detection capabilities_

## Multiple Files

If you want to divide the code into multiple files, you will get include errors.

To surpass this, you will need to move the files you want to include into the Nicla Vision USB drive, found in the file explorer.

## Troubleshooting

- Ensure the Nicla Vision firmware is up to date via OpenMV IDE
- Check WiFi credentials if streaming fails
- Adjust detection parameters for different lighting conditions
- Verify ToF sensor is not obstructed for accurate distance readings
