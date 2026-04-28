import serial
import time
import sys
import select
import termios
import tty

PORTS = ["/dev/ttyACM1", "/dev/ttyACM2"]
BAUD = 115200

history = []  # last 3 tracks


def connect():
    for port in PORTS:
        try:
            ser = serial.Serial(port, BAUD, timeout=0.05)
            time.sleep(2)
            print(f"[OK] Connected to {port}")
            return ser
        except Exception:
            continue

    print("[ERR] Could not connect")
    sys.exit(1)


def send(ser, cmd):
    if not cmd.endswith("\n"):
        cmd += "\n"
    ser.write(cmd.encode())
    print(f">>> {cmd.strip()}")


def reverse_track(track):
    parts = track.split(',')
    parts = list(reversed(parts))

    reversed_parts = []

    for p in parts:
        p = p.strip()

        if p.startswith('F'):
            reversed_parts.append('B' + p[1:])
        elif p.startswith('B'):
            reversed_parts.append('F' + p[1:])
        elif p.startswith('L'):
            reversed_parts.append('R' + p[1:])
        elif p.startswith('R'):
            reversed_parts.append('L' + p[1:])
        else:
            reversed_parts.append(p)

    return ",".join(reversed_parts)


def read_loop(ser, loop_mode=False):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    emergency_latched = False

    try:
        while True:
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)

                if ch.lower() == 'x':
                    send(ser, "X")

                    if loop_mode:
                        print("\n[LOOP TERMINATED]")
                        return True  # signal break to loop mode
                    else:
                        print("\n[EMERGENCY LATCHED]")
                        emergency_latched = True

                elif ch.lower() == 'c':
                    if emergency_latched:
                        print("\n[EMERGENCY CLEARED]")
                        send(ser, "0")
                        emergency_latched = False

                elif ch.lower() == 'q':
                    print("\n[PAUSE/RESUME]")
                    send(ser, "q")

            line = ser.readline()
            if line:
                decoded = line.decode(errors="ignore").strip()
                print(decoded)

                if "[AUTO] Track complete." in decoded:
                    return False

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_track():
    global history

    print("\n--- Last Tracks ---")
    if not history:
        print("(none)")
    else:
        for i in range(len(history)):
            print(f"{i+1}: {history[-(i+1)]}")

    print("\nEnter Track (or press 1/2/3):")
    choice = input("> ").strip()

    if choice.isdigit():
        idx = int(choice) - 1
        if idx < len(history):
            selected = history[-(idx+1)]
            print(f"[INFO] Using: {selected}")
            return selected
        else:
            print("[WARN] Invalid selection")
            return None

    if not choice:
        return None

    history.append(choice)
    if len(history) > 3:
        history.pop(0)

    return choice


def main():
    ser = connect()
    last_track = None

    try:
        while True:
            mode = input("\nLoop track? (y/n): ").strip().lower()
            loop_mode = (mode == 'y')

            track = get_track()
            if not track:
                continue

            last_track = track

            if loop_mode:
                print("[INFO] Loop mode enabled (press x to stop)")
                while True:
                    send(ser, f"T:{last_track}")
                    terminated = read_loop(ser, loop_mode=True)
                    if terminated:
                        break
            else:
                send(ser, f"T:{last_track}")
                read_loop(ser, loop_mode=False)

                action = input("\nEnter = new | r = repeat | b = backward: ").strip().lower()

                if action == 'r':
                    print("[INFO] Repeating...")
                    send(ser, f"T:{last_track}")
                    read_loop(ser, loop_mode=False)

                elif action == 'b':
                    rev = reverse_track(last_track)
                    print(f"[INFO] Backward track: {rev}")
                    send(ser, f"T:{rev}")
                    read_loop(ser, loop_mode=False)

    finally:
        ser.close()
        print("[INFO] Closed")


if __name__ == "__main__":
    main()
