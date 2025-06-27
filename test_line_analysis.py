import cv2
import numpy as np
from picamera2 import Picamera2
import test_line_detection as ld  # local helper module

# -------------------------- PARAMETERS ---------------------------------
FRAME_SIZE = ld.FRAME_SIZE
TURN_OFFSET_FRAC = 0.10   # 10 % of image width
LOOP_CIRCULARITY = 0.80   # area/perimeter² threshold for a loop
LOOP_MIN_AREA    = 3_000  # px² – ignore tiny circles

# ----------------------------------------------------------------------
#  Detector helpers
# ----------------------------------------------------------------------
def detect_turn(mask: np.ndarray) -> str | None:
    """Return 'left', 'right', or None based on bottom‑strip centroid."""
    h, w = mask.shape
    bottom = mask[int(h * 0.75):, :]             # lowest 25 % of image
    M = cv2.moments(bottom)
    if M["m00"] == 0:
        return None
    cx = M["m10"] / M["m00"]
    centre = w / 2
    offset = w * TURN_OFFSET_FRAC
    if cx < centre - offset:
        return "left"
    if cx > centre + offset:
        return "right"
    return None


def detect_loop(contours) -> bool:
    """True if any contour looks like a closed loop."""
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < LOOP_MIN_AREA:
            continue
        peri = cv2.arcLength(cnt, True)
        if peri == 0:
            continue
        circularity = 4 * np.pi * area / (peri ** 2)
        if circularity >= LOOP_CIRCULARITY:
            return True
    return False


def detect_discontinuity(contours) -> bool:
    """True when multiple separate line fragments are visible."""
    return len(contours) > 1

# ----------------------------------------------------------------------
#  Main camera loop
# ----------------------------------------------------------------------

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": FRAME_SIZE})
    picam2.configure(config)
    picam2.start()

    try:
        while True:
            frame_rgb = picam2.capture_array()

            # Low‑level segmentation (from helper module)
            mask      = ld.get_line_mask(frame_rgb)
            contours  = ld.find_line_contours(mask)

            # High‑level interpretation
            turn_dir      = detect_turn(mask)
            loop_present  = detect_loop(contours)
            gaps_present  = detect_discontinuity(contours) and not loop_present

            # Visualisation --------------------------------------------------
            mask = ld.get_line_mask(frame_rgb)
            status_strings = []
            if turn_dir:
                status_strings.append(f"TURN {turn_dir.upper()}")
            if loop_present:
                status_strings.append("LOOP")
            elif gaps_present:
                status_strings.append("GAP(S)")
            if not status_strings:
                status_strings.append("STRAIGHT")

            status_text = " | ".join(status_strings)
            cv2.putText(mask, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            cv2.imshow("Mask", mask)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
