import argparse
import os
import serial
import time
import datetime

parser = argparse.ArgumentParser(
    description="Read ADC samples from the Arduino over serial and write a CSV."
)
parser.add_argument("--port", default="COM3", help="serial port, e.g. COM3")
parser.add_argument("--baud", type=int, default=115200, help="baud rate")
parser.add_argument("--n", type=int, required=True, help="number of samples to collect")
parser.add_argument("--out", required=True, help="output CSV path")
parser.add_argument("--note", default="", help="free text, stored in the CSV header")
args = parser.parse_args()

folder = os.path.dirname(args.out)
if folder:
    os.makedirs(folder, exist_ok=True)

with serial.Serial(args.port, args.baud, timeout=1) as ser:
    time.sleep(2)
    ser.reset_input_buffer()

    for _ in range(5):
        ser.readline()

    data = []
    bad_lines = 0
    consecutive_bad = 0

    try:
        while len(data) < args.n:
            try:
                line = ser.readline().decode(errors="ignore").strip()
                t_str, raw_str = line.split(",")
                data.append((int(t_str), int(raw_str)))
                consecutive_bad = 0

                if len(data) % 1000 == 0:
                    print(f"{len(data)} / {args.n}")

            except (ValueError, IndexError):
                bad_lines += 1
                consecutive_bad += 1
                if consecutive_bad > 50:
                    print("50 malformed lines in a row - is the board still connected?")
                    break

    except KeyboardInterrupt:
        print("\ninterrupted - writing what has been collected so far")

if data:
    duration_us = data[-1][0] - data[0][0]
    duration_s = duration_us / 1e6
    mean_interval_us = duration_us / (len(data) - 1) if len(data) > 1 else 0.0
    rate_sps = (len(data) - 1) / duration_s if duration_s > 0 else 0.0
else:
    duration_s = 0.0
    mean_interval_us = 0.0
    rate_sps = 0.0

stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(args.out, "w", newline="") as f:
    f.write("# ADC noise capture\n")
    f.write(f"# date: {stamp}\n")
    f.write(f"# port: {args.port}, baud: {args.baud}\n")
    f.write("# source: A0 trimmer potentiometer on the 511/512 code boundary\n")
    f.write(f"# requested samples: {args.n}, received: {len(data)}, bad lines: {bad_lines}\n")
    f.write(f"# duration_s: {duration_s:.3f}, effective_rate_sps: {rate_sps:.1f}, mean_interval_us: {mean_interval_us:.1f}\n")
    f.write(f"# note: {args.note}\n")
    f.write("sample_index,t_us,raw\n")
    for i, (t_us, raw) in enumerate(data):
        f.write(f"{i},{t_us},{raw}\n")

print()
print(f"samples:        {len(data)} of {args.n} requested")
print(f"bad lines:      {bad_lines}")
print(f"duration:       {duration_s:.3f} s")
print(f"effective rate: {rate_sps:.1f} samples/s")
print(f"mean interval:  {mean_interval_us:.1f} us")
print(f"written to:     {args.out}")
