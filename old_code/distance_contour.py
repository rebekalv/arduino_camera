import sensor, image, time
from machine import I2C
from vl53l1x import VL53L1X

# Camera setup
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # lower resolution = less memory
sensor.skip_frames(time=2000)

# ToF setup
i2c = I2C(2)
tof = VL53L1X(i2c)

clock = time.clock()

# Parameters
OFFSET = 30
MIN_AREA = 200
MIN_PIXELS = 200

while True:
    clock.tick()
    img = sensor.snapshot()

    # ToF distance
    dist = tof.read()
    img.draw_string(2, 2, f"Dist: {dist} mm", color=(255, 255, 255), scale=1)

    # Dynamic threshold
    stats = img.get_statistics()
    mean_val = stats.l_mean()
    low = max(0, mean_val - OFFSET)

    # Binary mask
    img.binary([(0, low)])
    img.erode(1)
    img.dilate(2)

    # --- ROI for edge detection (center zone only) ---
    roi_size = 60
    roi = (
        img.width()//2 - roi_size//2,
        img.height()//2 - roi_size//2,
        roi_size,
        roi_size
    )
    edges = img.find_edges(image.EDGE_CANNY, threshold=(50, 80), roi=roi)
    img.draw_rectangle(roi, color=200)  # draw ROI box for debugging

    # Blobs
    blobs = img.find_blobs([(0, 127)], pixels_threshold=MIN_PIXELS, area_threshold=MIN_AREA, merge=True)

    if blobs:
        cx_ref = img.width() // 2
        cy_ref = img.height() // 2

        target = None
        nearest_dist = float("inf")

        for b in blobs:
            dx = b.cx() - cx_ref
            dy = b.cy() - cy_ref
            d = (dx*dx + dy*dy) ** 0.5
            if d < nearest_dist:
                nearest_dist = d
                target = b

        if target:
            img.draw_rectangle(target.rect(), color=(255, 0, 0), thickness=2)
            img.draw_cross(target.cx(), target.cy(), color=(0, 255, 0))
