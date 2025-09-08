import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # easier detection
sensor.set_framesize(sensor.QVGA)       # 320x240
sensor.skip_frames(time=2000)
clock = time.clock()

width = 320
zone_left = width // 3
zone_right = 2 * width // 3

# Parameters
MIN_AREA = 200       # ignore tiny blobs
MAX_AREA = 20000     # ignore blobs that cover most of the frame
OFFSET = 30          # threshold offset around mean brightness

while True:
    clock.tick()
    img = sensor.snapshot()

    # Dynamic background: measure current brightness
    stats = img.get_statistics()
    mean_val = stats.l_mean()  # average luminance
    low = max(0, mean_val - OFFSET)
    high = min(255, mean_val + OFFSET)

    thresholds = [(0, low)]  # treat darker-than-background as obstacle
    # alternatively: thresholds = [(high, 255)]  # treat brighter-than-background

    blobs = img.find_blobs(thresholds, area_threshold=MIN_AREA, pixels_threshold=MIN_AREA)

    nearest = None
    nearest_area = 0

    for b in blobs:
        area = b.w() * b.h()
        if MIN_AREA < area < MAX_AREA:
            if area > nearest_area:
                nearest = b
                nearest_area = area

    if nearest:
        cx = nearest.cx()
        cy = nearest.cy()

        # Draw blob
        img.draw_rectangle(nearest.rect(), color=127)
        img.draw_cross(cx, cy, color=255)

        # Decide zone
        if cx < zone_left:
            zone = "LEFT"
        elif cx < zone_right:
            zone = "CENTER"
        else:
            zone = "RIGHT"

        print("Nearest obstacle:", zone, "area:", nearest_area, "mean brightness:", mean_val)

        # Draw zone dividers
        img.draw_line((zone_left, 0, zone_left, 240), color=200)
        img.draw_line((zone_right, 0, zone_right, 240), color=200)

    print(clock.fps(), "fps")
