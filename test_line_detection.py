import cv2
import numpy as np

# ---------------------- GENERAL PARAMETERS -----------------------------
FRAME_SIZE        = (640, 480)   # Camera resolution (width, height)
MIN_SEGMENT_AREA  = 1_500        # Minimum area (px) for a line fragment

# Morphological kernels
OPEN_KERNEL  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
CLOSE_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

# ----------------------------------------------------------------------
#  Public helper functions
# ----------------------------------------------------------------------
def get_line_mask(frame_rgb, *, min_segment_area: int = MIN_SEGMENT_AREA) -> np.ndarray:
    """Return a binary mask (uint8, 0/255) of all qualifying line fragments."""
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Morphological cleaning
    clean = cv2.morphologyEx(th, cv2.MORPH_OPEN,  OPEN_KERNEL, iterations=1)
    clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, CLOSE_KERNEL, iterations=2)

    # Component filtering – keep every blob above *min_segment_area*
    num, labels, stats, _ = cv2.connectedComponentsWithStats(clean, connectivity=8)
    mask = np.zeros_like(clean, dtype=np.uint8)
    for i in range(1, num):                  # skip background label 0
        if stats[i, cv2.CC_STAT_AREA] >= min_segment_area:
            mask[labels == i] = 255
    return mask


def find_line_contours(mask: np.ndarray, *, min_segment_area: int = MIN_SEGMENT_AREA):
    """Return contours whose area ≥ *min_segment_area*."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cnt for cnt in contours if cv2.contourArea(cnt) >= min_segment_area]


# ----------------------------------------------------------------------
#  Demonstration loop (run only when executed directly)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    from picamera2 import Picamera2

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": FRAME_SIZE})
    picam2.configure(config)
    picam2.start()

    try:
        while True:
            frame_rgb = picam2.capture_array()
            mask      = get_line_mask(frame_rgb)
            contours  = find_line_contours(mask)
            disp      = draw_segments(frame_rgb, contours)

            cv2.imshow("Mask", mask)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
