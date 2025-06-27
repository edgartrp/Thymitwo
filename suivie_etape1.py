import time
from gpiozero import DigitalInputDevice
import NAV_CONTROL as nav  # forward, backward, turn, stop, read_sensors, kill_all

# --- CONFIGURATION CONSTANTS ---
NEUTRAL_ANGLE = 90
MAX_LEFT_ANGLE = 140
MAX_RIGHT_ANGLE = 40

LOW_SPEED = 24
MID_SPEED = 26
MAX_SPEED = 30

BACK_SPEED = 18
LITTLE_ANGLE = 15
MID_ANGLE = 30
BIG_ANGLE = 45

DELAY = 0.1
LOOP_INTERVAL = 0.01

# Flags for contre-braquage
cb_left = False
cb_right = False

def line_position(l, m, r, prev):
    """Retourne -1 si ligne a gauche, 0 si centre, 1 si a droite."""
    global cb_left, cb_right

    if cb_left:
        cb_left = False
        return -1
    elif cb_right:
        cb_right = False
        return 1
    elif l == 0 and m == 1 and r == 0:
        return 0
    elif (l == 1 and m == 0 and r == 0) or (l == 1 and m == 1 and r == 0):
        return -1
    elif (l == 0 and m == 0 and r == 1) or (l == 0 and m == 1 and r == 1):
        return 1
    else:
        return prev


def main():
    global cb_left, cb_right

    nav.turn(NEUTRAL_ANGLE)
    nav.stop()

    line_prev = 0
    line_pos = 0

    try:
        while True:
            l, m, r = nav.read_sensors()  # 0 = noir, 1 = blanc
            line_pos = line_position(l, m, r, line_prev)
            print(f"Etat capteurs ? l={l}, m={m}, r={r}")


            # Out/In/Out -> ligne centre
            if l == 0 and m == 1 and r == 0:
                nav.turn(NEUTRAL_ANGLE)
                nav.forward(MID_SPEED)

            # Ajustements leves
            elif l == 1 and m == 1 and r == 0:
                nav.turn(NEUTRAL_ANGLE + LITTLE_ANGLE)
                nav.forward(MID_SPEED)
            elif l == 0 and m == 1 and r == 1:
                nav.turn(NEUTRAL_ANGLE - LITTLE_ANGLE)
                nav.forward(MID_SPEED)

            # Ajustements moyens
            elif l == 1 and m == 0 and r == 0:
                nav.turn(NEUTRAL_ANGLE + MID_ANGLE)
                nav.forward(LOW_SPEED)
            elif l == 0 and m == 0 and r == 1:
                nav.turn(NEUTRAL_ANGLE - MID_ANGLE)
                nav.forward(LOW_SPEED)

            # 3 capteurs hors ligne -> contre-braquage
            elif l == 0 and m == 0 and r == 0:
                time.sleep(DELAY)
                if l == 0 and m == 0 and r == 0:
                    nav.stop()

                    if line_pos == 0:
                        angle = NEUTRAL_ANGLE
                        nav.turn(angle)
                        nav.backward(BACK_SPEED)
                        while True:
                            _, m2, _ = nav.read_sensors()
                            if m2 == 1:
                                break
                            time.sleep(LOOP_INTERVAL)

                    elif line_pos == -1:
                        print("CB, ligne a gauche")
                        cb_left = True
                        angle = NEUTRAL_ANGLE - BIG_ANGLE
                        nav.turn(angle)
                        nav.backward(BACK_SPEED)
                        # attente retour centre
                        while True:
                            _, m2, _ = nav.read_sensors()
                            if m2 == 1:
                                break
                            time.sleep(LOOP_INTERVAL)
                        nav.stop()
                        nav.turn(NEUTRAL_ANGLE + LITTLE_ANGLE)
                        nav.forward(LOW_SPEED)

                    elif line_pos == 1:
                        print("CB, ligne a droite")
                        cb_right = True
                        angle = NEUTRAL_ANGLE + BIG_ANGLE
                        nav.turn(angle)
                        nav.backward(BACK_SPEED)
                        # attente retour centre
                        while True:
                            _, m2, _ = nav.read_sensors()
                            if m2 == 1:
                                break
                            time.sleep(LOOP_INTERVAL)
                        nav.stop()
                        nav.turn(NEUTRAL_ANGLE - LITTLE_ANGLE)
                        nav.forward(LOW_SPEED)

                    print("fin CB")

            # mise a jour et pause
            line_prev = line_pos
            time.sleep(LOOP_INTERVAL)

    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")

    finally:
        nav.stop()
        nav.turn(NEUTRAL_ANGLE)
        nav.kill_all()
        time.sleep(10)
        print("\nFin du programme")


if __name__ == '__main__':
    main()
