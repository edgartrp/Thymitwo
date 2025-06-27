import NAV_CONTROL as nav
import HEAD_CONTROL as head
from time import sleep

CENTER, SIDE = 90, 90          # servo angles
RIGHT, LEFT  = 45, 135         # turn angles
THRESHOLD    = 150             # mm
PAUSE        = 0.05            # s
SPEED        = 20
HEAD_ID      = 1
CLEAR_HITS   = 3               # consecutive clear reads

def measure(angle):
    head.turn(HEAD_ID, angle)
    dist = head.measure_distance()
    sleep(PAUSE)
    return dist

def scan_sides():
    right = measure(CENTER - SIDE)
    left = measure(CENTER + SIDE)
    head.turn(HEAD_ID, CENTER)
    return left, right

def align_to_side(side):
    angle = CENTER + SIDE if side == 'left' else CENTER - SIDE
    while measure(angle) >= THRESHOLD:      # still not next to it
        nav.forward(SPEED)

def follow_side(side):
    angle = CENTER + SIDE if side == 'left' else CENTER - SIDE
    clear = 0
    while clear < CLEAR_HITS:               # still alongside
        clear = clear + 1 if measure(angle) >= THRESHOLD else 0
        nav.forward(SPEED)

def avoid(side):
    first, back = (LEFT, RIGHT) if side == 'right' else (RIGHT, LEFT)
    nav.turn(first)                         # step aside
    align_to_side(side)                     # get parallel
    follow_side(side)                       # hug obstacle
    nav.turn(back)                          # restore heading

def main():
    try:
        head.turn(HEAD_ID, CENTER)
        head.turn(2, CENTER)
        nav.turn(CENTER)
        nav.forward(SPEED)
        while True:
            dist = head.measure_distance()
            if dist < THRESHOLD:
                nav.stop()
                left, right = scan_sides()
                if right < THRESHOLD <= left:
                    avoid('left')
                elif left < THRESHOLD <= right:
                    avoid('right')
                else:
                    # camera tells us just ttesting w right
                    avoid('right')
            sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        nav.kill_all()
        head.kill_all()

if __name__ == "__main__":
    main()
