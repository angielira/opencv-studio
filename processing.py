"""Image-processing functions for OpenCV Studio (all OpenCV, no Streamlit).

Every function takes and returns BGR / BGRA uint8 images, like cv2.imread does.
"""
import cv2
import numpy as np


# ---------------- 1. Image arithmetic: brightness, contrast, clipping ----------------
def adjust(img, brightness=0, contrast=1.0, clip=True):
    """Brightness with cv2.add / cv2.subtract, contrast with cv2.multiply.

    clip=True  -> values are capped at 0..255 (the correct way).
    clip=False -> values above 255 wrap around (e.g. 288 -> 32), which is the
                  overflow bug from the notebook, so users can see it happen.
    """
    f = np.float64(img)
    ones = np.ones(img.shape, dtype='float64')
    f = cv2.multiply(f, ones, scale=contrast)                 # contrast
    shift = np.ones(img.shape, dtype='float64') * abs(brightness)
    f = cv2.add(f, shift) if brightness >= 0 else cv2.subtract(f, shift)   # brightness
    if clip:
        return np.uint8(np.clip(f, 0, 255))
    return (f.astype(np.int64) % 256).astype(np.uint8)   # uint8 wrap-around, same as np.uint8() in the notebook


# ---------------- 2. Thresholding ----------------
THRESH_METHODS = ['Global', 'Global (inverse)', 'Otsu (automatic)',
                  'Adaptive (mean)', 'Adaptive (Gaussian)']


def threshold(img, method='Global', thresh=127, block_size=25, c=10):
    """Returns (binary_image, threshold_used). Adaptive methods return None for the value."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    block_size = max(3, int(block_size) | 1)                   # must be odd and >= 3
    if method == 'Global':
        t, out = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
    elif method == 'Global (inverse)':
        t, out = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)
    elif method == 'Otsu (automatic)':
        t, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == 'Adaptive (mean)':
        t, out = None, cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                             cv2.THRESH_BINARY, block_size, c)
    elif method == 'Adaptive (Gaussian)':
        t, out = None, cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, block_size, c)
    else:
        raise ValueError(method)
    return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR), t


# ---------------- 3. Alpha channel: background remover ----------------
def remove_background(img, thresh=230, light_background=True, use_otsu=False, opacity=255):
    """Build a mask with thresholding, flip it with bitwise_not, attach it with merge.

    Returns (bgra_image, mask). The subject keeps alpha 255 (solid). The background
    gets alpha 255 - opacity: 0 (fully transparent) when opacity=255, and partly
    see-through for smaller values (opacity=127 gives 128, like the notebook's kangaroo).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    flag = cv2.THRESH_BINARY + (cv2.THRESH_OTSU if use_otsu else 0)
    t, bg = cv2.threshold(gray, thresh, opacity, flag)          # background -> opacity
    if not light_background:                                     # dark background instead
        bg = np.where(bg > 0, 0, opacity).astype(np.uint8)
    mask = cv2.bitwise_not(bg)                                   # subject -> 255, bg -> 255-opacity
    b, g, r = cv2.split(img)
    return cv2.merge([b, g, r, mask]), mask


def checkerboard(shape, size=16):
    """Grey checkerboard (BGR) used to show transparency."""
    h, w = shape[:2]
    board = ((np.indices((h, w)) // size).sum(0) % 2) * 60 + 180
    return cv2.merge([board.astype(np.uint8)] * 3)


def composite(bgra, background):
    """Paint a BGRA image over a BGR background using its alpha channel."""
    a = bgra[:, :, 3:4].astype(np.float32) / 255.0
    out = bgra[:, :, :3].astype(np.float32) * a + background.astype(np.float32) * (1 - a)
    return out.astype(np.uint8)


# ---------------- 4. Drawing and annotation ----------------
FONTS = {'Simplex': cv2.FONT_HERSHEY_SIMPLEX, 'Plain': cv2.FONT_HERSHEY_PLAIN,
         'Duplex': cv2.FONT_HERSHEY_DUPLEX, 'Complex': cv2.FONT_HERSHEY_COMPLEX,
         'Triplex': cv2.FONT_HERSHEY_TRIPLEX, 'Script': cv2.FONT_HERSHEY_SCRIPT_SIMPLEX}


def hex_to_bgr(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (b, g, r)


def annotate(img, text='', font='Simplex', font_scale=1.0, color='#FFFFFF', thickness=2,
             position='Bottom', box=None, box_color='#FF00FF', circle=None, outline=True):
    """Caption with putText (centered), optional rectangle and circle.

    box    = (x1, y1, x2, y2) as fractions 0..1 of width/height, or None
    circle = (cx, cy, r) as fractions 0..1 (r is a fraction of the shorter side), or None
    """
    out = img.copy()
    h, w = out.shape[:2]
    if box is not None:
        x1, y1, x2, y2 = box
        cv2.rectangle(out, (int(x1 * w), int(y1 * h)), (int(x2 * w), int(y2 * h)),
                      hex_to_bgr(box_color), max(2, thickness), cv2.LINE_AA)
    if circle is not None:
        cx, cy, r = circle
        cv2.circle(out, (int(cx * w), int(cy * h)), int(r * min(w, h)),
                   hex_to_bgr(box_color), max(2, thickness), cv2.LINE_AA)
    if text:
        f = FONTS[font]
        (tw, th), base = cv2.getTextSize(text, f, font_scale, thickness)
        x = max(5, (w - tw) // 2)                                   # centered horizontally
        y = {'Top': th + 15, 'Middle': (h + th) // 2, 'Bottom': h - base - 15}[position]
        if outline:                                                # dark outline = readable anywhere
            cv2.putText(out, text, (x, y), f, font_scale, (0, 0, 0), thickness + 3, cv2.LINE_AA)
        cv2.putText(out, text, (x, y), f, font_scale, hex_to_bgr(color), thickness, cv2.LINE_AA)
    return out


def fit(img, max_side=1600):
    """Shrink very large uploads (phone photos) so the app stays fast."""
    h, w = img.shape[:2]
    s = max_side / max(h, w)
    return cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1 else img
