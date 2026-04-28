# Autonomous Track Controller (Loop + Manual Mode)

This script connects to a microcontroller over serial and sends motion “tracks” (command sequences). It supports:

* Manual execution
* Loop mode (continuous repeat until stopped)
* Track history (last 3)
* Reverse track execution
* Live control: pause/resume and emergency stop

---

## Requirements

* Python 3
* `pyserial`

Install dependency:

```bash
pip3 install pyserial
```

---

## Setup

Update serial ports if needed:

```python
PORTS = ["/dev/ttyACM1", "/dev/ttyACM2"]
BAUD = 115200
```

Ensure your device is connected and accessible:

```bash
ls /dev/ttyACM*
```

---

## Run

```bash
sudo python3 roboCLI.py
```

---

## Track Format

Tracks are comma-separated motion commands:

```
F3,L90,F2,R90,B1
```

Where:

* `F` = Forward (distance in **meters**)
* `B` = Backward (distance in **meters**)
* `L` = Left turn (angle in **degrees**)
* `R` = Right turn (angle in **degrees**)

Example interpretation:

```
F3   → move forward 3 meters  
L90  → turn left 90 degrees  
B1   → move backward 1 meter  
```

---

## Modes

### 1. Loop Mode

At startup:

```
Loop track? (y/n):
```

If `y`:

* Track repeats indefinitely
* Stops only when `x` is pressed

### 2. Non-Loop Mode

If `n`:

* Track runs once
* Then prompts:

```
Enter = new | r = repeat | b = backward
```

---

## Controls (During Execution)

| Key | Action         |
| --- | -------------- |
| `x` | Emergency stop |
| `q` | Pause / Resume |

---

## Features

### Track History

Last 3 tracks are stored:

```
--- Last Tracks ---
1: F3,L90,F2
2: F1,R45
```

Select by pressing:

```
1 / 2 / 3
```

---

### Reverse Track

Automatically reverses:

* Order of commands
* Directions:

  * `F ↔ B`
  * `L ↔ R`

Example:

```
Input:  F3,L90
Output: R90,B3
```

---

## Serial Protocol

Commands sent:

```text
T:<track>   → Execute track  
X           → Emergency stop  
q           → Pause/Resume  
```

Each command ends with newline `\n`.

---

## Example Session

```text
[OK] Connected to /dev/ttyACM1

Loop track? (y/n): y

Enter Track:
> F3,L90

[INFO] Loop mode enabled (press x to stop)

>>> T:F3,L90
[AUTO] Track started.
[AUTO] Track complete.

>>> T:F3,L90
...
```

Press:

```
x
```

To stop loop.

---

## Notes

* Script uses non-blocking keyboard input (Linux terminal)
* Requires a real TTY (may not work inside some IDE consoles)
* Tested on Ubuntu

---
