# Working Notes

Internal notes on the current state of work.

---

## Fri 2026-08-21 — in progress

Resumed after a ten day break. Day 3 of the project.

**Plan**

- [✓] Clean up the working tree, fix line endings
- [✓] Work through the ADC chapter of the datasheet
- [ ] Walk through both analysis scripts from day 2 until every line is explainable
- [ ] Operating point check after 14 days
- [ ] Measurement 1: noise and distribution
- [ ] Measurement 3: resolution, precision, accuracy
- [ ] Correct the averaging law section of the README

### Line endings normalised

The working tree showed seven modified files and 1487 changed lines with no content
difference — `git diff --ignore-all-space` was empty. An editor had converted every file
from LF to CRLF. Committing that would have produced a commit that changes every line of
the repository and says nothing.

A stale `.git/index.lock`, dated 20.08. 17:04 and zero bytes, blocked every writing git
command while `git status` still worked — status only reads, checkout writes. Deleted
after confirming with `git status` that no merge or rebase was pending.

Fixed with a `.gitattributes` containing `* text=auto eol=lf`, which pins the repository
representation to LF regardless of what the local editor does. `git add --renormalize .`
afterwards reported no changes, so the already committed files were LF all along and the
problem was purely local.

Commits: `Normalise line endings to LF`, `Fix sketch folder names in documentation`
(the sketch folders are `pin_scan_led` and `pin_scan_button`, singular; NOTES and the
roadmap had them in the plural, which would break for anyone following the docs).

### Datasheet, ADC chapter

Document 7810D–AVR–01/15, automotive edition. Written up in `docs/datasheet_notes.md`
with section and page for every figure. The points that matter for this project:

**Conversion timing (sect. 23.4, p. 208–209).** A normal conversion is 13 ADC clock
cycles, the first one after enabling the ADC is 25. Full 10-bit resolution requires an
ADC clock between 50 and 200 kHz. The Arduino core uses a prescaler of 128, which at
16 MHz gives 125 kHz — the smallest available divisor that stays inside the limit, since
16 MHz / 64 would give 250 kHz. One cycle is 8 µs, so a conversion is 13 × 8 = **104 µs**.

The figure quoted everywhere for `analogRead()` is 112 µs, exactly one ADC clock cycle
more. That difference is library overhead: setting ADMUX, starting the conversion,
polling the flag, reading two registers. This is a prediction to be tested in
measurement 4 part A — a loop of 1000 reads without serial output should take ~112 ms.

**Accuracy (sect. 28.9, table 28-8, p. 262).** TUE 2.2 LSB typical / 3.5 max, INL 0.6/1.5,
DNL 0.3/0.7, gain and offset error ±3.5 each, all at Vcc = Vref = 4.0 V. Resolution
10 bits at ADC clock 200 kHz, −40 °C to +125 °C, 2.70–5.50 V.

All systematic, therefore untouched by averaging. Against the 0.0054 LSB repeatability
measured here that is a factor of about 400 — and the two numbers do not conflict,
because one is a fixed offset and the other a statistical spread. The chain is highly
precise and of unverified accuracy.

Two conditions worth keeping straight. The errors are specified at 4.0 V while this
board runs at a nominal 5 V, so they are indicative rather than directly applicable.
And the 200 kHz clock is attached to the *Resolution* row only: at 125 kHz this project
sits inside the 50–200 kHz window and below the specified point, which is the safe
direction — a slower clock gives the sample-and-hold capacitor more settling time.

**DNL deserves its own line.** 0.3 LSB typical, 0.7 max. Every result here depends on how
often the 511/512 boundary is crossed, and the fraction at code 511 is read as a measure
of where the input sits between the two codes — which assumes nominal code width. With
DNL up to 0.7 LSB that assumption is not guaranteed. It does not touch the noise or
averaging results (ratios, the code width cancels), but it limits how precisely the
operating point can be stated in absolute terms.

**Input circuitry (sect. 23.6.1, p. 212).** Sample-and-hold capacitor 14 pF, series
resistance 1–100 kΩ, recommended source impedance 10 kΩ or less. Sampling happens
1.5 ADC clocks after conversion start, i.e. 12 µs at 125 kHz.

The trimmer is 2 kΩ as a divider, so the impedance seen from the wiper is at most
1 kΩ in parallel with 1 kΩ = **500 Ω**, twenty times inside the recommendation. That is
the quantitative reason A0 reads cleanly while the unconnected A5 gave σ = 36.5 LSB.
Section 28.2 (p. 259) adds the missing piece for the floating pins: up to 1 µA of input
leakage per I/O pin, with no defined path to any potential.

**Bandgap reference (table 28-4, p. 261).** 1.0 V min, 1.1 V typical, 1.2 V max at
Vcc = 5 V, i.e. **±9 %**. Selected as an input channel with `MUX3:0 = 1110`
(table 23-4, p. 218); the reference selection bits are REFS1:0 in ADMUX (table 23-3,
p. 217), Arduino default `01` = AVcc.

This caps the planned VREF determination before it starts. Vcc = 1.1 V × 1024 / reading
inherits the ±9 % directly, so even a perfect reading gives a supply voltage known only
to ±9 %. It is a plausibility check, not a multimeter replacement, and it has to be
written up that way.

**Noise canceler (sect. 23.6, p. 211).** Runs a conversion with the CPU halted in sleep
mode. Not usable here — the acquisition is transmission-bound and the CPU has to keep
the UART fed. Goes into the README as an improvement, not into the measurements.

**Also noted, for the hardware demonstration later.** Section 23.6.2 point d: digital
pins ADC[3..0] must not switch while a conversion is in progress. No LEDs run during
acquisition today, so it does not apply yet — but the planned LED demonstration does
exactly that, and the effect should be measured rather than assumed.

**Temperature sensor (sect. 23.8, p. 215).** `MUX3:0 = 1000`, needs the 1.1 V reference,
sensitivity ~1 LSB/°C, accuracy ±10 °C. Not useful for the drift question: a sensor with
±10 °C accuracy cannot resolve the temperature changes that would have to correlate with
a 0.187 LSB step. Recorded because it is the obvious thing to reach for.

### Question 6 — where the datasheet and the measurements appear to disagree

*Sigma smaller than the quantization limit.* Measured σ = 0.176 LSB is below the
theoretical 1 LSB/√12 = 0.289 LSB. Not a contradiction: the √12 figure assumes the input
sweeps the full range so the rounding error is uniform over one step. Here the operating
point is static on a code boundary, the error is two-valued rather than uniform, and a
lopsided two-level distribution has a smaller variance — √(p(1−p)) = 0.175 for
p = 0.0317, which is exactly what was measured.

The consequence matters more than the observation: a small σ does not mean sub-step
resolution. A single sample still returns 511 or 512. This is why `log2(1024/σ)` must
not be used here — it reports 12.5 effective bits from a 10-bit converter, because its
precondition (σ larger than one quantization step) is violated.

*Precision beats specified accuracy by ~400×.* No conflict, see above.

*104 µs vs 112 µs.* One ADC clock of library overhead, to be measured directly.

*The ~4.95 Hz component.* Reproduced on three independent 50 000-sample segments, lags
152/160 repeating at 304/312 and 456/464. The datasheet offers no mechanism. Decidable
by changing the sampling interval and seeing whether the peak stays at 4.95 Hz (physical)
or moves (alias). Left open until that test is run.

### README changes made today

- New subsection under *Sources of Error*: absolute accuracy from the datasheet, and why
  it does not conflict with the measured precision
- *Reference voltage not yet verified* extended with the ±9 % bandgap tolerance and the
  register details for the method
- *ADC channel crosstalk* now quotes the 14 pF capacitor, the 12 µs sampling window, the
  500 Ω source impedance of the trimmer and the 1 µA leakage figure
- New section *What Would Be Done Differently With More Time*
- *Repository Contents* lists `docs/datasheet_notes.md`

### Still open at this point in the day

- Everything from Block 2 onwards: Python walkthrough, operating point, measurements
- **The averaging law section of the README is still wrong** and must be corrected today.
  The 0.025 LSB floor is an artefact of the single 0.187 LSB step; see the day 3 plan.

---

## Mon 2026-08-10 — complete

**Plan**

- [✓] Re-run the noise pre-test on A0 and confirm the working point is still around
   140 / 60. If not, re-adjust the trimmer to the code boundary before anything else.
   Nothing recorded afterwards is comparable if this step is skipped.
- [✓] Verify the serial path from Python before writing anything larger
      (`python/porttest.py`).
- [✓] Write `python/logger.py`: open the serial port, wait 2 s, flush the input buffer,
   read lines and write a CSV with columns `sample_index`, `t_us`, `raw`.
   Count malformed lines instead of crashing.
- [✓] Two 1000-sample runs recorded, reproducibility checked.
- [✓] First plot: raw value over sample index, axis labels and units, saved to `docs/`.
- [✓] Record at least 800 000 samples in one run for Tuesday's averaging analysis.

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

**`logger.py` written (18:35)**

Takes `--port`, `--baud`, `--n`, `--out` and `--note`. Creates the target directory,
opens the port, waits 2 s, flushes, discards five lines, then reads until `n` valid
samples are collected. Malformed lines are counted rather than fatal; fifty malformed
lines in a row abort the run on the assumption that the board has been disconnected.
`Ctrl+C` is caught around the loop so that a long capture can be stopped without
losing what has been collected. Writes a `#`-prefixed metadata header followed by
`sample_index,t_us,raw`, then prints a summary.

Verification run, `--n 20`:

```
samples:        20 of 20 requested
bad lines:      0
duration:       0.019 s
effective rate: 980.4 samples/s
mean interval:  1020.0 us
```

The mean interval matches the prediction of 12 characters x 85.0 us exactly. The
duration corresponds to 19 intervals rather than 20, confirming that the rate is
computed over `n-1` gaps.

**Two 1000-sample runs (18:40 and 19:15)**

```
run 1: 1000 samples, 0 bad lines, 1.059 s, 943.0 sps, mean interval 1060.5 us
run 2: 1000 samples, 0 bad lines, 1.059 s, 943.0 sps, mean interval 1060.4 us
```

| | run 1 | run 2 |
| :--- | ---: | ---: |
| count 511 / 512 | 171 / 829 | 163 / 837 |
| mean [LSB] | 511.829 | 511.837 |
| sigma [LSB] | 0.3765 | 0.3694 |

Sigma differs by 1.9 %, the mean by 0.008 LSB. Both are within what 1000 samples of a
two-level process produce by chance, so the setup is reproducible. Cross-check against
sqrt(p(1-p)): 0.171 gives 0.37651, 0.163 gives 0.36936 — agreement to four decimals.

The fraction at code 511 continues to fall: 0.205 at 12:40, 0.171 at 18:40, 0.163 at
19:15. The mean rises correspondingly. Same direction as the weekend shift, no
reversal.

**The digit transition is visible inside one file**

The mean interval of 1060.5 us in run 1 occurs nowhere in the data. The individual
intervals take exactly two values, 1020 us and 1105 us, with nothing in between. The
transition sits at t = 1 000 000 us, where the timestamp gains its seventh digit:
about 523 of the 999 intervals fall before it and 476 after, which reproduces the
observed mean to within a microsecond.

This is stronger evidence for the transmission-bound behaviour than the earlier
comparison of two separate runs, and it settles the case for padding the timestamp
before the main measurement.

**Sketch rebuilt for constant line length (19:30)**

`adc_logger` now formats each sample with `snprintf(buf, sizeof(buf), "%09lu,%03d", t_us, raw)`.
The timestamp is still read before `analogRead()`; the formatting happens afterwards
and does not affect it.

The USB replug planned for this block was dropped. Opening the port from Python
resets the board over DTR, so `micros()` starts near zero on every capture anyway —
confirmed by the first timestamp being ~464000 us in three separate runs hours apart.
The 71.6 minute wraparound is unreachable with 17 minute captures.

**Main run, 800 000 samples (19:45-20:02)**

```
samples:        800000 of 800000 requested
bad lines:      0
duration:       1021.363 s
effective rate: 783.3 samples/s
mean interval:  1276.7 us
```

Predicted 1275.0 us from 15 characters at 85.0 us; measured 1276.7, a deviation of
0.13 %. Zero bad lines over 800 000 lines.

Distribution over the whole run:

| code | count | fraction |
| ---: | ---: | ---: |
| 511 | 25 344 | 0.03168 |
| 512 | 774 495 | 0.96814 |
| 513 | 161 | 0.00020 |

mean 511.9685, sigma 0.1758. Cross-check sqrt(p(1-p)) with p = 0.03168 gives 0.1752;
the remainder comes from the 513s.

The fraction at 511 has fallen from 0.205 at 12:40 to 0.032. The dither is much weaker
than at the start of the day. This does not invalidate the averaging analysis —
Var(mean of N) = p(1-p)/N holds exactly for any p — but it does mean sigma is small in
absolute terms, and it raises the question of how long the operating point remains
usable at all.

The appearance of code 513 is new. It means the signal crossed the *next* code
boundary at times, i.e. drifted by more than a full quantization step.

**Drift structure within the main run**

Split into ten segments of 80 000 samples (102 s each):

```
seg  mean       n(511)  n(513)
0    511.97469   2045   20
1    511.97278   2198   20
2    511.97189   2262   13
3    511.97267   2202   16
4    511.97155   2294   18
5    511.97085   2346   14
6    511.97135   2301    9
7    511.97205   2249   13
8    511.97267   2201   15
9    511.93471   5246   23
```

Segments 0-8 span 15 minutes and vary by 0.004 LSB. The setup is therefore stable to
better than 0.005 LSB over a quarter of an hour — the long drift seen across the day
does not appear on this timescale.

Segment 9 is different. Narrowing it down in 8000-sample slices (10 s) and then in
1000-sample slices (1.3 s) locates a single discrete step: the mean falls from 511.971
to 511.785, a change of **0.187 LSB**, and stays at the new level. The transition
occurs entirely between two adjacent 1.3 s slices, with no intermediate value, at
approximately sample 784 000, i.e. t = 1001 s, about 20 s before the end of the run.

The step is 95 standard errors of an 8000-sample mean, so it is not a statistical
artefact. Nobody was at the bench at the time.

*What it cannot be.* A change in supply voltage is excluded by the topology: the
trimmer is a divider from the same 5 V that supplies AVCC, so the conversion is
ratiometric and the supply cancels out of the result. Temperature is excluded by the
shape — thermal effects ramp, they do not step.

*Working hypothesis.* The divider ratio itself changed, i.e. something moved
mechanically at the wiper contact. That is consistent with the slow monotonic drift
across three days: a trimmer set on Friday relaxing, with occasional discrete
micro-slips. Stated as a hypothesis, not a result.

Three timescales are now quantified:

| timescale | observation |
| :--- | :--- |
| 3 days | +0.67 LSB, monotonic |
| 15 minutes | stable to better than 0.005 LSB |
| single event | 0.187 LSB step in under 1.3 s |

Resolution limit worth noting: the signal has only two states, so a change shows up
only as a change in the *frequency* of code 511 and is visible only through a windowed
mean. Shorter windows give better time resolution but a noisier estimate — at 1000
samples the standard error is 0.006 LSB against a 0.187 LSB step, at 100 samples it is
0.018. This is a property of the measurement, not of the analysis code.

**First figures (21:40-22:20)**

`python/analysis/plot_timeseries.py` reads a capture, counts its own header lines,
and writes a raw time series plus a moving-average figure. It runs over both committed
example captures, so the four figures in `docs/` can be regenerated by anyone who
clones the repository.

```
data/example_variable_interval.csv   18:45:39   mean 511.8290  sigma 0.3765   17.1 % at 511
  moving average spans 511.6875 to 511.9531
data/example_noise_1k.csv            20:40:38   mean 511.9630  sigma 0.1888    3.7 % at 511
  moving average spans 511.9219 to 512.0000
```

Both sigma values check out against sqrt(p(1-p)): 0.171 gives 0.3765, 0.037 gives
0.1888.

Three things came out of looking at the figures.

*The moving average is itself quantized.* Over a window of N samples of a two-level
signal the mean can only take values k/N, so the curve is a staircase with a step
height of 1/64 = 0.0156 LSB. Averaging does not remove quantization, it moves it from
1 LSB to 1/N LSB. That is the project's central claim, visible directly in a figure.

*The span of the moving average shows when dither stops working.* At 17.1 % the average
never reaches 512 — every window of 64 contains at least one 511, so every window
carries information. At 3.7 % it reaches exactly 512.0000, meaning some windows held no
511 at all and returned the bare code. Dither degrades gracefully and then stops, not
because the mathematics changes but because the boundary crossings run out. This is a
concrete argument for keeping the operating point close to a 50/50 split.

*The step in the main run was not permanent.* The main run ended at 511.785; the
capture at 20:40 is back at 511.963. A thermal or electrical drift has a preferred
direction, a mechanical contact that slips and reseats does not. Consistent with the
micro-slip hypothesis, still not proof.

Figures written: `docs/timeseries_near_boundary.png`, `docs/dither_near_boundary.png`,
`docs/timeseries_drifted.png`, `docs/dither_drifted.png`.

Figure conventions adopted for the rest of the project: axis labels with units, y ticks
only at codes the converter can actually output, markers instead of lines for
two-level data, absolute tick labels (no matplotlib offset annotation), 150 dpi.

**Averaging law and autocorrelation (22:50-23:40)**

`python/analysis/analyse_main_run.py` folds the 800 000 samples into blocks of
1 to 16 384, takes the mean of each block and the standard deviation of those means,
and compares against sigma_1/sqrt(N). It then evaluates the autocorrelation of the
first 50 000 samples for lags 0 to 200, lag by lag as dot products rather than a full
O(n^2) correlation.

```
N        blocks   sigma_meas   sigma_theory   ratio
1        800000   0.175756     0.175756       1.000
2        400000   0.123808     0.124279       0.996
4        200000   0.091522     0.087878       1.041
8        100000   0.066604     0.062139       1.072
16        50000   0.052191     0.043939       1.188
32        25000   0.042140     0.031070       1.356
64        12500   0.035075     0.021970       1.597
128        6250   0.029823     0.015535       1.920
256        3125   0.027823     0.010985       2.533
512        1562   0.026684     0.007767       3.435
1024        781   0.026133     0.005492       4.758
2048        390   0.025039     0.003884       6.447
4096        195   0.024361     0.002746       8.871
8192         97   0.019570     0.001942      10.078
16384        48   0.004583     0.001373       3.338
```

**This is the main result of the day.** The 1/sqrt(N) law holds to within 7 % up to
N = 8 and then leaves the theory. From N = 128 onward the curve is flat: over a range
of 32 in block size, where theory predicts a fall by 5.7, the measured value moves only
from 0.0298 to 0.0244 LSB.

A floor independent of N is the signature of low-frequency noise. White noise averages
down by construction; noise with power rising towards low frequencies does not, because
a longer window admits correspondingly slower components. So averaging improves this
chain by a factor of about 7 - from 0.176 to roughly 0.025 LSB - and reaches that limit
after about 0.16 s (N = 128). Averaging longer buys nothing.

Not interpreted: the N = 16384 point. 48 blocks, 10 % uncertainty on the estimate
alone, and a block length of 21 s comparable to the timescale of the wander itself.
Needs more block sizes and possibly overlapping blocks on Tuesday.

Worth remembering when quoting numbers: sigma at N = 1 is the standard deviation of a
two-level process and measures boundary-crossing frequency, not noise amplitude. The
ratio column is meaningful, the absolute baseline is not.

**Autocorrelation**

```
50000 samples, lags 0..200
a 50 Hz disturbance would appear with a period of 15.67 samples
acf[1] = -0.0100, significance band +/- 0.0088
lags outside the band: [1, 3, 4, 5, 6, 7, 8, 9, 12, 14, 15, 16, 18, 19, 20, 22, 24, 25, 26, 29] ...
```

Short-lag correlation is small: below about 0.03 up to lag ~140. More lags cross the
95 % band than chance would give, but the magnitudes are nowhere near enough to explain
a factor of 8 shortfall at N = 4096. The plateau is therefore a low-frequency effect,
not a sample-to-sample one. Worth stating explicitly, because sample correlation was
the obvious first suspect and it has now been ruled out with data.

No mains signature. The dotted guides at multiples of 15.67 samples do not line up with
the peaks.

Open: isolated peaks near lags 152 and 160 reaching 0.11 and 0.17, far outside the
band, corresponding to 194 and 204 ms or roughly 5 Hz. First check on Tuesday is
whether they reproduce on a different 50 000-sample segment. At a 3 % event rate the
autocorrelation is dominated by sparse crossings and isolated large values can arise
from that alone.

Figures: `docs/sqrt_n_law.png`, `docs/autocorrelation.png`.

---

## Carried over to Tuesday

- **Block 10, the control run.** `logger.py --n 500000 --out data/main_control.csv`.
  Not essential for measurements 1-3, but the fraction at code 511 fell from 0.205 to
  0.037 over one day; if that continues there may be no usable operating point left.
- **Walk through the Python.** `logger.py` was written step by step, but
  `plot_timeseries.py` and `analyse_main_run.py` were handed over finished under time
  pressure. Both need going through line by line before more analysis code is written,
  and the next script should be written from scratch again.
- **Measurements 1, 2 and 3** from the existing data.
- Recompute the autocorrelation on a second segment to test the 152/160 peaks.
- Decide whether to re-adjust the trimmer. Against: it breaks comparability with every
  number recorded so far. For: at 3.7 % crossings, some 64-sample windows already
  contain none at all.

**Open questions**

- What sets the 0.025 LSB floor? A 1/f-like contribution from the trimmer contact is
  the obvious candidate given the mechanical behaviour seen elsewhere, but nothing
  measured so far distinguishes it from a 1/f contribution of the converter or the
  supply.
- Histogram for measurement 1 will show two bars, not a bell curve. This needs to be
  addressed explicitly rather than presented as a flaw.
- Does an effective-resolution figure derived from the averaged sigma mean anything
  while VREF is unverified? Resolution and accuracy have to be kept apart.

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
- `arduino/pin_scan_led/` — cycles digital pins 2–13, used to identify the LEDs
- `arduino/pin_scan_button/` — reads pins 2–13 with `INPUT_PULLUP`, used to identify the buttons
- `arduino/noise_pretest/` — 200 samples, reports min/max/mean/sigma and a value tally
- `arduino/adc_logger/` — reads A0 and prints one line per sample as
  `micros(),analogRead(A0)`, i.e. elapsed time in µs and the raw ADC value, at
  115200 baud. The timestamp is taken on the Arduino; conversion to volts happens
  in Python.
- `python/porttest.py` — opens COM3, waits for the bootloader, flushes the buffer and
  prints ten lines. Used once to verify the serial path before writing `logger.py`.
- `data/example_noise_1k.csv` — 1000 samples in the final padded format, committed so
  the analysis can be reproduced without hardware.
- `data/example_variable_interval.csv` — 1000 samples from before the sketch change,
  kept as evidence for the two-valued sampling interval.
- `python/analysis/analyse_main_run.py` — averaging law and autocorrelation of the
  main run; writes `docs/sqrt_n_law.png` and `docs/autocorrelation.png`.
- `python/analysis/plot_timeseries.py` — reads a capture and writes a raw time series
  and a moving-average figure; runs over both example captures.
- `python/logger.py` — the acquisition tool. Command line arguments for port, baud
  rate, sample count, output path and a free-text note; writes a CSV with a metadata
  header and reports the effective sampling rate.