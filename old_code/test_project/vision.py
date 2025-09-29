import sensor, image, time
import utils

# Init sensor
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
clock = time.clock()

width = 320
MIN_AREA, MAX_AREA, OFFSET = 200, 20000, 30

def process_frame():
    clock.tick()
    img = sensor.snapshot()

    low, high, mean_val = utils.dynamic_threshold(img.get_statistics(), OFFSET)
    thresholds = [(0, low)]  # darker-than-background

    blobs = img.find_blobs(thresholds, area_threshold=MIN_AREA, pixels_threshold=MIN_AREA)

    nearest = None
    nearest_area = 0
    for b in blobs:
        if utils.is_valid_blob(b, MIN_AREA, MAX_AREA):
            area = b.w() * b.h()
            if area > nearest_area:
                nearest = b
                nearest_area = area

    info = {"zone": None, "area": 0, "brightness": mean_val}

    if nearest:
        cx = nearest.cx()
        cy = nearest.cy()
        img.draw_rectangle(nearest.rect(), color=127)
        img.draw_cross(cx, cy, color=255)
        zone = utils.get_zone(cx, width)
        info.update({"zone": zone, "area": nearest_area, "brightness": mean_val})

    return img, info
