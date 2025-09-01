from PIL import Image
import numpy as np
from scipy.ndimage import generic_filter

def green_ratio(pixel):
    r, g, b = pixel[:3]
    total = r + g + b + 1e-5
    return g / total

def classify_pixel(pixel, strong_thresh=0.6, weak_thresh=0.4):
    ratio = green_ratio(pixel)
    if ratio > strong_thresh:
        return 2  # strong green
    elif weak_thresh < ratio <= strong_thresh:
        return 1  # blurred/edge green
    return 0  # non-green

def detect_greenscreen_blur(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    pixels = np.array(img)

    # classify all pixels
    mask = np.apply_along_axis(classify_pixel, 2, pixels)
    
    # find edges between green (1/2) and non-green (0)
    def local_edge(values):
        return (np.any(values > 0) and np.any(values == 0))
    edge = generic_filter((mask > 0).astype(int), local_edge, size=3)

    # Build visualization: red for blurred edge, keep rest transparent
    output = np.zeros_like(pixels)
    
    #output[edge == 1] = [255, 0, 0, 255]
    output[edge == 1] = pixels[edge == 1]  # keep original color
    result = Image.fromarray(output, mode="RGBA")
    result.save(output_path, "PNG")

