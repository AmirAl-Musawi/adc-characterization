# Working Notes

Internal notes on the current state of work.

---

## Mon 2026-08-10 — in progress

**Plan**

- [✓] Re-run the noise pre-test on A0 and confirm the working point is still around
   140 / 60. If not, re-adjust the trimmer to the code boundary before anything else.
   Nothing recorded afterwards is comparable if this step is skipped.
- [✓] Verify the serial path from Python before writing anything larger
      (`python/porttest.py`).
- [ ] Write `python/logger.py`: open the serial port, wait 2 s, flush the input buffer,
   read lines and write a CSV with columns `sample_index`, `t_us`, `raw`.
   Count malformed lines instead of crashing.
- [ ] First plot: raw value over sample index, axis labels and units, saved to `docs/`.
- [ ] Record at least 800 000 samples in one run for Tuesday's averaging analysis.

**Working point check**

Operating point verified at 12:40 before any recording: still on the 511/512 code
boundary, but the split has shifted from 141/59 to 41/159 (mean 511.795, sigma 0.405
LSB, 200 samples). Trimmer deliberately left untouched — all Monday measurements use
this operating point.

The shift of +0.5 LSB in the mean over three days is a drift observation, not a fault:
the source moved closer to code 512 while the noise amplitude itself is unchanged.
The lower sigma follows directly from the split — for a two-level process
sigma = sqrt(p·(1−p)), and p = 41/200 = 0.205 gives 0.404 against the reported 0.405.
Sigma here measures how often the boundary is crossed, not how large the noise is,
so it is at its maximum at a 50/50 split and falls off towards either side.

Raw output — A0, 2026-08-10 (12:40):

```
=== Ergebnis Rausch-Vorabtest ===
Samples:        200
Minimum:        511
Maximum:        512
Spannweite:     1
Mittelwert:     511.795
Sigma (LSB):    0.405

Wert : Anzahl
511 : 41
512 : 159
Verschiedene Werte insgesamt: 2
=== Ende ===
```

**Logger sanity check (12:48, Arduino serial monitor)**

`adc_logger` verified in the serial monitor before handing the port to Python:

```
3173324,512
3174432,511
3175536,512
```

Intervals of 1108 and 1104 us. Both are multiples of 4 us, confirming the 4 us
resolution of `micros()` on the ATmega328P and an unmodified timer prescaler.

**Serial path verified from Python (13:05, `python/porttest.py`)**

First script of the project. Opens COM3 at 115200 baud with `timeout=1`, waits 2 s,
flushes the input buffer, reads ten lines and prints them. Output:

```
462336,512
463356,511
464376,511
465396,512
466416,512
467436,512
468456,512
469476,512
470496,512
```

Format correct, timestamps monotonic, only codes 511 and 512, no malformed line.

Two things fall out of this that were not being looked for.

*The 2 s warm-up is correctly sized, but only just.* The first timestamp is 462336 us,
so the sketch had been running for 0.46 s when Python started reading. Opening the
port pulls DTR low and resets the board; the bootloader therefore takes about 1.54 s,
leaving 0.46 s of margin. This is the quantitative justification for discarding the
first five lines in `logger.py`.

*The sample interval is set by the serial link, not by the converter.* All timestamp
differences are exactly 1020 us — not approximately, exactly. The serial monitor
reading half an hour earlier gave 1104-1108 us. The difference is one character:
the timestamp was seven digits then and six digits here.

At 16 MHz with U2X the UART divisor is UBRR = 16, giving an actual bit rate of
16 000 000 / (8 x 17) = 117 647 baud rather than the nominal 115 200, an error of
+2.1 %. One character is 10 bits (start, 8 data, stop), i.e. 85.0 us. The line
`462336,512\r\n` is 12 characters: 12 x 85.0 = 1020.0 us.

The agreement is exact, which means two things. First, the baud rate error has been
measured from the data alone, without an oscilloscope. Second, the ~112 us ADC
conversion is entirely hidden behind the transmission — the acquisition loop is
transmission-bound. That is the answer to measurement 4, arriving two days early.

**Consequence: the sampling rate is not constant**

Over a 15-minute run `micros()` grows from one digit to nine. The line grows with it
and the interval steps up by 85 us per digit:

| timestamp digits | chars/line | interval | rate |
| :--- | ---: | ---: | ---: |
| 1 (start of run) | 7 | 595 us | 1680 /s |
| 6 | 12 | 1020 us | 980 /s |
| 9 (from t = 100 s) | 15 | 1275 us | 784 /s |

About 89 % of a 15-minute run sits at nine digits. The 886 /s figure calculated on
Friday and the 904 /s observed this morning are therefore both snapshots of a moving
quantity, not a constant.

**Decision: pad the timestamp to a fixed width**

Before the main run, `adc_logger` is changed to emit the timestamp zero-padded to
nine digits and the ADC code to three, using `snprintf` with `"%09lu,%03d"`. Every
line is then 15 characters and the interval is a constant 1275 us, i.e. 784.3
samples/s.

The reason is not cosmetic. Uniform sampling is a precondition for the
autocorrelation analysis: with a variable interval the lag axis has no fixed time
unit, and a periodic disturbance would smear across lags instead of showing up as a
clean period. The cost is five minutes of sketch editing. The variable-rate
behaviour is kept as a documented result, not discarded.

Revised expectations for the main run: 800 000 samples take about 17 minutes and
produce roughly 17-18 MB. The control run of 500 000 samples takes about 11 minutes.

**Open questions**

- Will the 800 000-sample run show more than two distinct codes? Over several minutes
  slow drift should widen the distribution — the difference between short-term noise
  and long-term stability is expected to be the main result of measurement 2.
- Histogram for measurement 1 will show two bars, not a bell curve. This needs to be
  addressed explicitly rather than presented as a flaw.
- Does the measured 784.3 samples/s hold over the full run once the line length is
  fixed? Any deviation is now attributable to the host side, since the Arduino side
  is constant by construction.

---

## Fri 2026-08-07 — complete

**Done**

- [✓] All tools installed (Arduino IDE, Git, VS Code, Python packages)
- [✓] Blink running → toolchain verified
- [✓] Git repository created locally and on GitHub, first commits pushed
- [✓] Pin assignment determined
- [✓] Noise pre-test carried out
- [✓] ADC logger sketch written and verified in the serial monitor

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
  than one quantization step, so the converter only toggles between two adjacent
  codes. The mean therefore carries sub-LSB information — this is dither, and it is
  what makes the averaging law demonstrable.
- A1 offers no advantage over A0 and depends on ambient light, which is not
  controllable.
- A5 has by far the most noise, but its excursions are too large to be thermal noise
  alone. Coupled interference from the environment is the likely cause; mains hum is
  the obvious candidate, though this was not verified. Interference of any periodic
  origin is correlated between successive samples and therefore does not average down
  as 1/sqrt(N), which would break measurement 2. Kept as a comparison data point only.

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

- `arduino/pin_scan_analog/` — scans A0–A5, used to identify the potentiometer and the LDR
- `arduino/pin_scan_leds/` — cycles digital pins 2–13, used to identify the LEDs
- `arduino/pin_scan_buttons/` — reads pins 2–13 with `INPUT_PULLUP`, used to identify the buttons
- `arduino/noise_pretest/` — 200 samples, reports min/max/mean/sigma and a value tally
- `arduino/adc_logger/` — reads A0 and prints one line per sample as
  `micros(),analogRead(A0)`, i.e. elapsed time in µs and the raw ADC value, at
  115200 baud. The timestamp is taken on the Arduino; conversion to volts happens
  in Python.
- `python/porttest.py` — opens COM3, waits for the bootloader, flushes the buffer and
  prints ten lines. Used once to verify the serial path before writing `logger.py`.