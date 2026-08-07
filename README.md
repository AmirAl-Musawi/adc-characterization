# ADC Measurement Chain — Characterizing the ATmega328P ADC

Measurement and analysis of the analog-to-digital converter (ADC) of an Arduino UNO:
noise, averaging law, effective resolution, sampling rate.

**Status:** work in progress (day 1 of 7)

## Setup

_(to be added)_

## Hardware

Arduino UNO (ATmega328P) with an experimenter shield attached.

**Components on the shield:**

- 1 trimmer potentiometer (blue, 2 kΩ, adjusted with a flathead screwdriver) — signal source for all measurements
- 1 LDR (light dependent resistor) — second analog input
- 7 single LEDs: 3 red, 2 yellow, 2 green
- 1 RGB LED (red/green/blue in one package, occupies three digital pins)
- 2 momentary push buttons (no latching switches)
- Series resistors for all LEDs

## Pin Assignment

**Analog inputs**

| Component | Pin | Note |
| :--- | :--- | :--- |
| Trimmer potentiometer | A0 | primary signal source |
| LDR | A1 | responds to ambient light |

**Digital pins — LEDs**

| Component | Pin |
| :--- | :--- |
| LED red 1 | 2 |
| LED red 2 | 5 |
| LED red 3 | 8 |
| LED yellow 1 | 3 |
| LED yellow 2 | 7 |
| LED green 1 | 4 |
| LED green 2 | 6 |
| RGB LED, green channel | 9 |
| RGB LED, red channel | 10 |
| RGB LED, blue channel | 11 |

**Digital pins — buttons**

| Component | Pin | Note |
| :--- | :--- | :--- |
| Button 1 | 12 | `INPUT_PULLUP`, pressed = LOW |
| Button 2 | 13 | `INPUT_PULLUP`, pressed = LOW |

> Pins 0 and 1 are left unused — they are occupied by the serial interface.
> This leaves 12 digital pins (2–13), exactly as many as the shield requires.

## Measurements

_(to be added)_

## Sources of Error

### Reference voltage not yet verified

All raw ADC values are converted to voltage assuming VREF = 5.00 V. In practice the
USB supply typically delivers 4.6–5.1 V, so the absolute voltage scale carries a
systematic error of up to about 8 %.

This does not affect the core results: noise, the averaging law and the effective
resolution are all expressed in LSB (least significant bits), where the reference
voltage cancels out. Only the conversion to millivolts is uncertain.

VREF will be determined without a multimeter using the internal 1.1 V bandgap
reference of the ATmega328P.

### ADC channel crosstalk on floating inputs

The ATmega328P has a single ADC shared between all analog channels through a
multiplexer. Each conversion charges an internal sample-and-hold capacitor to the
input voltage. On a high-impedance input — an unconnected pin being the extreme
case — there is not enough charge transfer to fully settle the capacitor within the
sampling window, so the reading retains part of the previous channel's value.

This was observed directly while identifying the pin assignment. Covering the LDR
on A1 changed not only A1 but every subsequent channel, with the effect decaying
along the scan order:

| Channel | bright | dark | difference |
| :--- | ---: | ---: | ---: |
| A1 (LDR) | ~890 | ~37 | 853 |
| A2 (floating) | ~710 | ~172 | 538 |
| A3 (floating) | ~566 | ~198 | 368 |
| A4 (floating) | ~447 | ~248 | 199 |
| A5 (floating) | ~385 | ~256 | 129 |

Each channel retains roughly 60–65 % of the previous channel's excursion. A genuine
signal would appear on one channel only; the monotonic decay identifies the effect
as capacitive carryover rather than crosstalk in the wiring.

The datasheet recommends a source impedance below 10 kΩ for this reason. All
measurements in this project use the trimmer potentiometer on A0, which is read
first in every scan and has a low enough source impedance to be unaffected.