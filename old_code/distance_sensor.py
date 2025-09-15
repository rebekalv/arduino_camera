import sensor, image, time
from machine import I2C
from vl53l1x import VL53L1X

# Camera setup
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # grayscale for detection
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# ToF (time of flight) setup
i2c = I2C(2)
tof = VL53L1X(i2c)

clock = time.clock()

# Parameters BLOB DETECTION
THRESHOLD_TYPE = "dark"  # "dark" or "bright"
min_area = 200       # ignore tiny blobs
min_pixels = 200     # ignore tiny blobs
OFFSET = 30  # threshold offset around mean brightness

while True:
    clock.tick()
    img = sensor.snapshot()

    ## DISTANCE SENSOR
    dist = tof.read()  # Read distance
    img.draw_string(10, 10, f"Distance: {dist} mm", color=(255, 255, 255),scale=1.5) # Show distance on stream

    ## BLOB DETECTION

    # Dynamic background brightness
    stats = img.get_statistics()
    mean_val = stats.l_mean()
    if THRESHOLD_TYPE == "dark":
       limit = max(0, mean_val - OFFSET)
       thresholds = [(0, limit)]
    else:
       limit = min(255, mean_val + OFFSET)
       thresholds = [(limit, 255)]

    # Find dark or light blobs
    blobs = img.find_blobs(thresholds, pixels_threshold=min_pixels, area_threshold=min_area)

    if blobs:
            # Center of the image (where ToF points)
            center_x = img.width() // 2
            center_y = img.height() // 2

            # Find the blob covering the ToF line-of-sight
            target = None
            for b in blobs:
                if b.x() <= center_x <= b.x()+b.w() and b.y() <= center_y <= b.y()+b.h():
                    target = b
                    break
            if not target:
                # If no blob covers the center, find the nearest blob
                nearest = None
                nearest_dist = float('inf')
                for b in blobs:
                    # Calculate distance from blob center to image center
                    dx = b.cx() - center_x
                    dy = b.cy() - center_y
                    distance = (dx*dx + dy*dy)**0.5
                    if distance < nearest_dist:
                        nearest = b
                        nearest_dist = distance
                target = nearest

            if target:
                # Draw bounding box and mark as nearest object
                img.draw_rectangle(target.rect(), color=(255, 0, 0), thickness=3)
                img.draw_cross(target.cx(), target.cy(), color=(0, 255, 0))


