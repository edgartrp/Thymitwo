import threading
import time
import test_obstacles
import test_suivi_ligne
import NAV_CONTROL as nav
import HEAD_CONTROL as head

# Shared synchronization primitives
_lock = threading.Lock()
_resume_event = threading.Event()
_resume_event.set()  # line-following runs initially

# Wrap NAV_CONTROL methods to enforce mutual exclusion and pausing
def _wrap_nav_method(name):
    orig = getattr(nav, name)
    def wrapped(*args, **kwargs):
        if threading.current_thread().name == 'LineThread':
            _resume_event.wait()      # pause line thread during obstacle stop
        with _lock:                  # serialize all nav calls
            return orig(*args, **kwargs)
    return wrapped

for _name in ('forward', 'backward', 'turn', 'stop', 'read_sensors', 'kill_all'):
    setattr(nav, _name, _wrap_nav_method(_name))

# Wrap HEAD_CONTROL methods similarly
def _wrap_head_method(name):
    orig = getattr(head, name)
    def wrapped(*args, **kwargs):
        if threading.current_thread().name == 'LineThread':
            _resume_event.wait()      # pause line thread during obstacle stop
        with _lock:                  # serialize all head calls
            return orig(*args, **kwargs)
    return wrapped

for _name in ('turn', 'measure_distance', 'kill_all'):
    setattr(head, _name, _wrap_head_method(_name))


def _line_thread():
    # Delegate to existing line-following script
    test_suivi_ligne.main()


def _obstacle_thread():
    # Continuously check distance and stop robot on detection
    while True:
        dist = test_obstacles.head.measure_distance()
        if dist < test_obstacles.THRESHOLD:
            _resume_event.clear()      # pause line-following
            test_obstacles.nav.stop()  # stop robot immediately
            print("obstacle ahead")
            # wait until obstacle clears before resuming
            while test_obstacles.head.measure_distance() < test_obstacles.THRESHOLD:
                time.sleep(0.1)
                print("obstacle ahead")
            _resume_event.set()        # resume line-following
        time.sleep(0.2)


def main():
    t_line = threading.Thread(target=_line_thread, name='LineThread', daemon=True)
    t_obs  = threading.Thread(target=_obstacle_thread, name='ObsThread',  daemon=True)
    t_line.start()
    t_obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        nav.kill_all()
        head.kill_all()


if __name__ == '__main__':
    main()
