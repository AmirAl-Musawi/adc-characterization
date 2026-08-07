# Working Notes

Internal notes on the current state of work.

---

## Fri 2026-08-07

**Done**

- [✓] All tools installed (Arduino IDE, Git, VS Code, Python packages)
- [✓] Blink running → toolchain verified
- [✓] Git repository created locally and on GitHub, first commits pushed
- [ ] Pin assignment determined
- [ ] Noise pre-test carried out

**COM port:** COM3

**Pin assignment**

| Component | Pin |
| :--- | :--- |
| Trimmer potentiometer | A0 |
| LDR | A1 |
| LED red 1 / 2 / 3 | 2 / 5 / 8 |
| LED yellow 1 / 2 | 3 / 7 |
| LED green 1 / 2 | 4 / 6 |
| RGB LED G / R / B | 9 / 10 / 11 |
| Button 1 / 2 | 12 / 13 |

**Noise pre-test**

- Distinct values: __
- Minimum / maximum: __ / __
- Sigma: __ LSB
- Verdict: plan A / plan B

Raw output:

- None

**Observation — pin 11 (RGB blue)**

During the button scan with `INPUT_PULLUP`, pins 2–10 each reported one spurious
"pressed" event at startup: the weak internal pull-up (20–50 kΩ) cannot hold the pin
above the logic threshold against an LED to ground, so the pin reads LOW. Pin 11 was
the only one that stayed HIGH, because the blue LED has a forward voltage of roughly
3.0–3.4 V versus 1.8–2.2 V for red/yellow/green. This confirms pin 11 as the blue
channel of the RGB LED.

**State of the code**

- `arduino/adc_logger/adc_logger.ino` sends `micros(),analogRead()` at 115200 baud

**Next step (Monday)**

- Write `python/logger.py`: open the serial port, wait 2 s, flush the input buffer,
  read lines and write a CSV with columns `sample_index`, `t_us`, `raw`

**Open questions**

- None