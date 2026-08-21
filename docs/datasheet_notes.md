# ATmega328P — ADC datasheet notes

**Source:** ATmega328P datasheet, document Atmel-7810 (automotive edition),
section 23 "Analog-to-Digital Converter", p. 205 ff.
https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf

## 1 — Converter accuracy
| Parameter | Symbol | Min | Typ | Max | Unit |
| :--- | :--- | ---: | ---: | ---: | :--- |
| Absolute accuracy | TUE | — | 2.2 | 3.5 | LSB |
| Integral non-linearity | INL | — | 0.6 | 1.5 | LSB |
| Differential non-linearity | DNL | — | 0.3 | 0.7 | LSB |
| Gain error | — | −3.5 | — | 3.5 | LSB |
| Offset error | — | −3.5 | — | 3.5 | LSB |

Conditions: Vcc = Vref = 4.0 V, ADC clock = ..., TA = ...

## 2 — Conversion timing

| Quantity | Value | Source |
| :--- | ---: | :--- |
| Normal conversion | 13 ADC clock cycles | sect. 23.4 |
| First conversion after enable | 25 ADC clock cycles | sect. 23.4 |
| Clock range for full 10-bit resolution | 50–200 kHz | sect. 23.4 |
| Prescaler used by the Arduino core | 128 | Arduino library default |

At 16 MHz the prescaler of 128 yields an ADC clock of 125 kHz, i.e. 8 µs per cycle.
A normal conversion therefore takes 13 × 8 µs = **104 µs**, the first one after
enabling the ADC 25 × 8 µs = 200 µs.

128 is the smallest available prescaler that keeps the ADC clock below the 200 kHz
limit: 16 MHz / 64 would give 250 kHz and violate the specification.

The commonly quoted figure for `analogRead()` is 112 µs, i.e. one ADC clock cycle
more than the conversion itself. The difference is the overhead of the library
function: setting ADMUX, starting the conversion, polling the completion flag and
reading two result registers.

## 3 — Input circuitry and source impedance

## 4 — Voltage references

## 5 — ADC Noise Reduction Mode

## 6 — Where datasheet and measurement disagree