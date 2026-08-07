# ADC-Messkette — Charakterisierung des ATmega328P-ADC

Messung und Auswertung des Analog-Digital-Wandlers (ADC) eines Arduino UNO:
Rauschen, Mittelungsgesetz, effektive Auflösung, Abtastrate.

**Status:** in Arbeit (Tag 1 von 7)

## Aufbau

_(folgt)_

## Hardware

Arduino UNO (ATmega328P) mit aufgestecktem Experimentier-Shield.

**Bestückung des Shields:**

- 1 Trimmpoti (blau, 2 kΩ, Einstellung per Schlitzschraubendreher) — Signalquelle für alle Messungen
- 1 LDR (Light Dependent Resistor, Fotowiderstand) — zweiter Analogeingang
- 7 Einzel-LEDs: 3 rot, 2 gelb, 2 grün
- 1 RGB-LED (rot/grün/blau in einem Gehäuse, belegt drei Digitalpins)
- 2 Taster (Tastfunktion, kein Rastschalter)
- Vorwiderstände für alle LEDs

## Pinbelegung

**Analogeingänge**

| Bauteil | Pin | Bemerkung |
| :--- | :--- | :--- |
| Trimmpoti | A? | Hauptsignalquelle |
| LDR | A? | reagiert auf Umgebungslicht |

**Digitalpins — LEDs**

| Bauteil | Pin |
| :--- | :--- |
| LED rot 1 | ? |
| LED rot 2 | ? |
| LED rot 3 | ? |
| LED gelb 1 | ? |
| LED gelb 2 | ? |
| LED grün 1 | ? |
| LED grün 2 | ? |
| RGB-LED, Kanal rot | ? |
| RGB-LED, Kanal grün | ? |
| RGB-LED, Kanal blau | ? |

**Digitalpins — Taster**

| Bauteil | Pin | Bemerkung |
| :--- | :--- | :--- |
| Taster 1 | ? | `INPUT_PULLUP`, gedrückt = LOW |
| Taster 2 | ? | `INPUT_PULLUP`, gedrückt = LOW |

> Pins 0 und 1 bleiben frei — sie werden von der seriellen Schnittstelle belegt.
> Damit stehen 12 Digitalpins (2–13) zur Verfügung, genau so viele wie das Shield benötigt.

## Messungen

_(folgt)_

## Fehlerquellen

_(folgt)_
