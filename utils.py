def dynamic_threshold(stats, offset=30):
    mean_val = stats.l_mean()
    low = max(0, mean_val - offset)
    high = min(255, mean_val + offset)
    return low, high, mean_val

def get_zone(cx, width=320):
    left = width // 3
    right = 2 * width // 3
    if cx < left:
        return "LEFT"
    elif cx < right:
        return "CENTER"
    else:
        return "RIGHT"

def is_valid_blob(blob, min_area=200, max_area=20000):
    area = blob.w() * blob.h()
    return min_area < area < max_area
