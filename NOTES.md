# Working Notes

Internal notes on the current state of work.

---

## Fri 2026-08-07

**Done**

- [✓] All tools installed (Arduino IDE, Git, VS Code, Python packages)
- [✓] Blink running → toolchain verified
- [✓] Git repository created locally and on GitHub, first commits pushed
- [✓] Pin assignment determined
- [✓] Noise pre-test carried out
- [ ] ADC logger sketch written and verified in the serial monitor

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

Three candidate signal sources were compared, 200 samples each, 5 ms apart
(total span ≈ 1 s per run). Short-term noise only — slow drift is not visible
over this interval.

| Source | distinct values | min / max | range | mean | sigma [LSB] |
| :--- | ---: | :--- | ---: | ---: | ---: |
| A0 trimmer potentiometer | 2 | 511 / 512 | 1 | 511.295 | **0.457** |
| A1 LDR | 2 | 409 / 410 | 1 | 409.775 | 0.419 |
| A5 floating input | many | 400 / 534 | 134 | 460.415 | 36.504 |

**Verdict: plan A. Working point is A0 at the 511/512 code boundary, sigma = 0.457 LSB.
Do not touch the trimmer.**

Reasoning:

- A0 sits almost exactly on a code boundary (141 / 59 split). The noise is smaller
  than one quantisation step, so the converter only toggles between two adjacent
  codes. The mean therefore carries sub-LSB information — this is dither, and it is
  what makes the averaging law demonstrable.
- A1 offers no advantage over A0 and depends on ambient light, which is not
  controllable.
- A5 has by far the most noise, but it is mains-borne interference at 50 Hz, i.e.
  periodic and correlated. Periodic interference does not average down as 1/sqrt(N),
  so it would break measurement 2. Kept as a comparison data point only.

Raw output — A0 (trimmer potentiometer, working point):

```
=== Ergebnis Rausch-Vorabtest ===
Samples:        200
Minimum:        511
Maximum:        512
Spannweite:     1
Mittelwert:     511.295
Sigma (LSB):    0.457

Wert : Anzahl
511 : 141
512 : 59
Verschiedene Werte insgesamt: 2
=== Ende ===
```

Raw output — A1 (LDR):

```
=== Ergebnis Rausch-Vorabtest ===
Samples:        200
Minimum:        409
Maximum:        410
Spannweite:     1
Mittelwert:     409.775
Sigma (LSB):    0.419

Wert : Anzahl
409 : 45
410 : 155
Verschiedene Werte insgesamt: 2
=== Ende ===
```

Raw output — A5 (floating input):

```
=== Ergebnis Rausch-Vorabtest ===
Samples:        200
Minimum:        400
Maximum:        534
Spannweite:     134
Mittelwert:     460.415
Sigma (LSB):    36.504
```

Cross-check: for a two-level process, sigma = sqrt(p·(1−p)). For A0, p = 59/200 =
0.295 gives 0.456 — the sketch reported 0.457. The distribution is Bernoulli, so the
measured sigma reflects how often the noise crosses the code boundary, not its
amplitude.

**Observation — pin 11 (RGB blue)**

During the button scan with `INPUT_PULLUP`, pins 2–10 each reported one spurious
"pressed" event at startup: the weak internal pull-up (20–50 kΩ) cannot hold the pin
above the logic threshold against an LED to ground, so the pin reads LOW. Pin 11 was
the only one that stayed HIGH, because the blue LED has a forward voltage of roughly
3.0–3.4 V versus 1.8–2.2 V for red/yellow/green. This confirms pin 11 as the blue
channel of the RGB LED.

**State of the code**

- `arduino/pin_analog/` — scans A0–A5, used to identify the potentiometer and the LDR
- `arduino/pin_leds/` — cycles digital pins 2–13, used to identify the LEDs
- `arduino/pin_buttons/` — reads pins 2–13 with `INPUT_PULLUP`, used to identify the buttons
- `arduino/rausch_vortest/` — 200 samples, reports min/max/mean/sigma and a value tally
- `arduino/adc_logger/` — in progress (block 6). Target output format:
  `micros(),analogRead(A0)`, one line per sample, 115200 baud.
  Timestamp is taken on the Arduino, conversion to volts happens in Python.
  **Replace this line once the sketch is uploaded and verified.**

**Next steps (Monday)**

1. Write `python/logger.py`: open the serial port, wait 2 s, flush the input buffer,
   read lines and write a CSV with columns `sample_index`, `t_us`, `raw`.
   Count malformed lines instead of crashing.
2. First plot: raw value over sample index, axis labels and units, saved to `docs/`.
3. Record at least 30 000 samples in one run for Tuesday's averaging analysis.

**Open questions**

- Will the 30 000-sample run show more than two distinct codes? Over several minutes
  slow drift should widen the distribution — the difference between short-term noise
  and long-term stability is expected to be the main result of measurement 2.
- Histogram for measurement 1 will show two bars, not a bell curve. This needs to be
  addressed explicitly rather than presented as a flaw.