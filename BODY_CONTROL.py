import time
from gpiozero import TonalBuzzer


# === Buzzer initialization ===
tb = TonalBuzzer(18) 

# === Buzzer functions ===
def play(tune):
    for note, duration in tune:
        tb.play(note)
        time.sleep(float(duration))
    tb.stop()

#Reconaissance vocale

#Telecommande ?

# === Main Test Function ===
def main() -> None:
    try:
        print("Testing single beep...")
        play([(440, 0.5)])
        time.sleep(1)

        print("Testing short melody...")
        melody = [(262, 0.3), (294, 0.3), (330, 0.3), (349, 0.3), (392, 0.3)]
        play(melody)
        time.sleep(1)

        print("Testing scale ascending...")
        scale_up = [(note, 0.2) for note in [262, 294, 330, 349, 392, 440, 494, 523]]
        play(scale_up)
        time.sleep(1)

        print("Testing scale descending...")
        scale_down = list(reversed(scale_up))
        play(scale_down)

    except Exception as e:
        print(f"Error during buzzer test: {e}")

    finally:
        tb.stop()
        print("Cleaning up and stopping buzzer...")
        tb.close()
        print("Buzzer test complete.")

if __name__ == "__main__":
    main()
