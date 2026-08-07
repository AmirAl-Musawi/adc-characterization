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
| Trimmer potentiometer | A_ |
| LDR | A_ |
| LED red 1 / 2 / 3 | _ / _ / _ |
| LED yellow 1 / 2 | _ / _ |
| LED green 1 / 2 | _ / _ |
| RGB LED R / G / B | _ / _ / _ |
| Button 1 / 2 | _ / _ |

**Noise pre-test**

- Distinct values: __
- Minimum / maximum: __ / __
- Sigma: __ LSB
- Verdict: plan A / plan B

Raw output:

- None

**State of the code**

- `arduino/adc_logger/adc_logger.ino` sends `micros(),analogRead()` at 115200 baud

**Next step (Monday)**

- Write `python/logger.py`: open the serial port, wait 2 s, flush the input buffer,
  read lines and write a CSV with columns `sample_index`, `t_us`, `raw`

**Open questions**

- None