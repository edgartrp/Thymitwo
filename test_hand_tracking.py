import sys
import signal
import numpy as np
import cv2

import HEAD_CONTROL as head        # provides servo_pan, servo_tilt, capture_frame, kill_all
import LED_CONTROL as led          # wheel LED helpers

# ─── Servo objects & limits ───────────────────────────────────────────
PAN_SERVO  = head.servo_pan
TILT_SERVO = head.servo_tilt
PAN_MIN_DEG,  PAN_MAX_DEG  = 20, 160
TILT_MIN_DEG, TILT_MAX_DEG = 45, 125
KP_PAN, KP_TILT = 50, 55
DEADZONE_PX     = 50
SMOOTHING       = 0.25

# ─── Skin‑colour mask params (YCrCb space) ───────────────────────────
Y_MIN, Y_MAX   =   0, 255
CR_MIN, CR_MAX = 135, 180
CB_MIN, CB_MAX =  85, 135

class HandTracker:
    def __init__(self):
        # Get one frame to read resolution
        init_frame = head.capture_frame()
        self.h, self.w = init_frame.shape[:2]
        self.cx, self.cy = self.w // 2, self.h // 2

        # Centre servos
        self.pan_angle  = 90
        self.tilt_angle = 90
        PAN_SERVO.angle, TILT_SERVO.angle = self.pan_angle, self.tilt_angle

        # LED state
        led.clear_light()
        self._hand_present = False

        # Morphology kernels
        self.kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        self.kernel_dil  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))

    # ─── helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _clamp(val, lo, hi):
        return max(lo, min(hi, val))

    def _update_servo(self, axis, error_px):
        if axis == 'pan':
            delta = -(KP_PAN * error_px / self.w)
            tgt   = self.pan_angle + delta
            self.pan_angle = (1 - SMOOTHING) * tgt + SMOOTHING * self.pan_angle
            self.pan_angle = self._clamp(self.pan_angle, PAN_MIN_DEG, PAN_MAX_DEG)
            PAN_SERVO.angle = self.pan_angle
        else:  # tilt
            delta = -(KP_TILT * error_px / self.h)
            tgt   = self.tilt_angle + delta
            self.tilt_angle = (1 - SMOOTHING) * tgt + SMOOTHING * self.tilt_angle
            self.tilt_angle = self._clamp(self.tilt_angle, TILT_MIN_DEG, TILT_MAX_DEG)
            TILT_SERVO.angle = self.tilt_angle

    # ─── main loop ────────────────────────────────────────────────────
    def run(self):
        try:
            while True:
                frame = head.capture_frame()
                if frame is None or frame.size == 0:
                    print("⚠️  Failed to capture frame – check camera.")
                    break

                # 1. Skin mask
                ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                mask = cv2.inRange(ycrcb, (Y_MIN, CR_MIN, CB_MIN), (Y_MAX, CR_MAX, CB_MAX))
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel_open, iterations=2)
                mask = cv2.dilate(mask, self.kernel_dil, iterations=2)

                # 2. Largest contour → hand centroid
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                hand_detected = False
                if cnts:
                    cnt = max(cnts, key=cv2.contourArea)
                    if cv2.contourArea(cnt) > 2000:
                        hand_detected = True
                        M = cv2.moments(cnt)
                        if M['m00']:
                            hx = int(M['m10'] / M['m00'])
                            hy = int(M['m01'] / M['m00'])
                            cv2.circle(frame, (hx, hy), 8, (0, 255, 0), -1)
                            ex, ey = hx - self.cx, hy - self.cy
                            if abs(ex) > DEADZONE_PX:
                                self._update_servo('pan',  ex)
                            if abs(ey) > DEADZONE_PX:
                                self._update_servo('tilt', ey)
                        cv2.drawContours(frame, [cnt], -1, (0, 255, 255), 2)

                # 3. LED feedback on state change
                if hand_detected != self._hand_present:
                    led.wheel_lighting() if hand_detected else led.clear_light()
                self._hand_present = hand_detected

                # 4. HUD overlays
                cv2.line(frame, (self.cx - 20, self.cy), (self.cx + 20, self.cy), (255, 255, 255), 1)
                cv2.line(frame, (self.cx, self.cy - 20), (self.cx, self.cy + 20), (255, 255, 255), 1)
                cv2.putText(frame, f"Pan  {self.pan_angle:3.0f}°",  (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
                cv2.putText(frame, f"Tilt {self.tilt_angle:3.0f}°", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

                cv2.imshow("Hand tracker – Picamera2", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    break
        finally:
            self.shutdown()

    def shutdown(self):
        print("↩︎  Centring servos & turning off LEDs …")
        PAN_SERVO.angle, TILT_SERVO.angle = 90, 90
        led.kill_all()
        head.kill_all()
        cv2.destroyAllWindows()

# ─── entry ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tracker = HandTracker()
    signal.signal(signal.SIGINT, lambda *a: tracker.shutdown() or sys.exit(0))
    tracker.run()
