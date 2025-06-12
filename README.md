# Thymitwo
Code related to the Solution Factory of EFREI's Master Camp

## Ultra Map

The `ultra_map.py` script rotates a servo and records distance measurements with an ultrasonic sensor. By default it sweeps from 0° to 180° in 10° steps and prints the mapping of angles to measured distances.

Run it with:

```bash
python3 ultra_map.py
```

Edit the script if you need to adjust the angle range, servo channel or GPIO pins used for the sensor.
