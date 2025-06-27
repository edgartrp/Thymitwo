import LED_CONTROL as led
import cv2
import numpy as np
from picamera2 import Picamera2

# ---------------------- GENERAL PARAMETERS -----------------------------
FRAME_SIZE = (640, 480)   # Camera resolution (width, height)
MIN_AREA   = 200_000      # Minimum mask area (px) to accept the object
STEP       = 16          # Quantisation step per RGB channel (0‑255)

# Morphological kernels
OPEN_KERNEL  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
CLOSE_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
ERODE_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

# ------------------------- UTILITY -------------------------------------

def quantise(value: float, step: int = STEP) -> int:
    """Clamp *value* to 0, step, 2*step, ... up to 255."""
    return int(round(value / step) * step) if value < 255 else 255

# -------------------- CAMERA INITIALISATION ----------------------------
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": FRAME_SIZE}
)
picam2.configure(config)
picam2.start()

# ------------------------------ LOOP -----------------------------------
try:
    while True:
        # 1) Capture (RGB order) ---------------------------------------
        frame_rgb = picam2.capture_array()

        # 2) Threshold (invert + Otsu) ---------------------------------
        gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, th = cv2.threshold(
            blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        # 3) Morphological cleaning ------------------------------------
        clean = cv2.morphologyEx(th, cv2.MORPH_OPEN, OPEN_KERNEL, iterations=2)
        clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, CLOSE_KERNEL, iterations=2)

        # 4) Keep the largest component --------------------------------
        num, labels, stats, _ = cv2.connectedComponentsWithStats(clean, connectivity=8)
        if num > 1:
            biggest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])  # ignore bg (0)
            mask = np.uint8(labels == biggest) * 255
        else:
            mask = clean

        area = cv2.countNonZero(mask)
        if area < MIN_AREA:
            # No reliable object detected; show debug and continue
            #cv2.imshow("Mask", mask)
            #cv2.imshow("Surface detection", frame_rgb)
            #if cv2.waitKey(1) & 0xFF == ord("q"):
                #break
            continue

        # 5) Light erosion to avoid edge pixels ------------------------
        inner_mask = cv2.erode(mask, ERODE_KERNEL, iterations=1)

        # 6) Color measurement (RGB order) -----------------------------
        b	, g, r, _ = cv2.mean(frame_rgb, mask=inner_mask)  # correct channel order!
        snap_rgb = tuple(quantise(c) for c in (r, g, b))

        # 7) Drive LEDs -------------------------------------------------
        print("snap_rgb sent to LED:", snap_rgb)
        led.all_led_color(*snap_rgb)

        # 8) Visual feedback ------------------------------------------
        frame_disp = frame_rgb  # for OpenCV display
        coords = cv2.findNonZero(mask)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            cv2.rectangle(frame_disp, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame_disp,
                f"{snap_rgb}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        # 9) Show windows ---------------------------------------------
        cv2.imshow("Mask", mask)
        cv2.imshow("Surface detection", frame_disp)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    # Graceful stop via CTRL‑C -----------------------------------------
    pass
finally:
    led.kill_all()
    picam2.stop()
    cv2.destroyAllWindows()
