"""
Description: Speedangle .sa to Racechrono .vbo format converter
Author: Tejinder Singh
Version : 0.0.1

TBD:
* Indentify coordinates for eastern and southern hemisphere and convert correctly
* Figure lean angle data to be read by RC
* Get Speedangle to log heading data
* Get Racechrono to .sa file import in the app

Reference:
SA log format definition on last 2 pages - http://www.speedangle.com/sauploads/2020/02/SpeedAngle-R4-APEX-R009-User-Manual-2019-0819.pdf
Converting to vbo coordinates - https://racelogic.support/01VBOX_Automotive/01General_Information/Knowledge_Base/VBOX_Latitude_and_Longitude_Calculations
VBO file format (not 100% accurate with RaceChrono) - https://racelogic.support/01VBOX_Automotive/01General_Information/Knowledge_Base/VBO_file_format#:~:text=VBOX%20data%20files%20are%20saved,as%20word%20processors%20or%20spreadsheets.&text=The%20%5Bcolumn%20names%5D%20parameter%20specifies,column%20of%20the%20data%20section.
"""


#!/usr/bin/env python3
import argparse
import datetime
import re
import sys
import time


def read_speedangle_file(input_file):
    ts_pattern = re.compile("^#D=.*")
    log_pattern = re.compile(
        "[0-9]{1,3}.[0-9]{6},-?[0-9]{1,3}.[0-9]{6},(-?[0-9]{1,3},){8}[F01]"
    )
    try:
        with open(input_file, "r") as f:
            lines = []
            for line in f:
                if log_pattern.match(line):
                    lines.append(line.strip("\n").split(","))
                elif ts_pattern.match(line):
                    log_timestamp = line.strip("\n=").split()[1]
    except FileNotFoundError as err:
        print(f"{err}\nCheck input filename")
        sys.exit(1)
    except PermissionError as err:
        print(f"{err}\nSeems you don't have permissions to read the input file")
        sys.exit(1)
    return log_timestamp, lines


def speedangle_to_racechrono_vbo(timestamp: str, sa_lines: list):
    rc_lines = []
    base_time = datetime.datetime.strptime(timestamp, "%H:%M:%S")
    for k, v in enumerate(sa_lines):
        line_time = float(
            f"{base_time + datetime.timedelta(milliseconds=k * 100)}".split()[
                1
            ].replace(":", "")
        )
        lat = float(v[0])
        lon = float(v[1])
        ang = float(v[2])
        accl = int(v[4])
        vel = float(v[6])
        sat = int(v[8])
        rc_lines.append(
            f"{sat:03} {line_time:6.2f} {lat*60:5.6f} {lon*-60:5.6f} {vel:3.2f} 000.00 00000.00 {accl:3.3f} 000.000 0000000.000 +010.000 {ang:3.3f} {accl:3.3f} 3 02.46"
        )
    return rc_lines


def write_racechrono_file(lines: list, output_file):
    rc_metadata = """[header]
satellites
time
latitude
longitude
velocity kmh
heading
height
long accel g
lat accel g
distance
device-update-rate
lean-angle
combined-acceleration g
fix-type
3d-precision

[column names]
sats time lat long velocity heading height longacc latacc distance device-update-rate lean-angle combined-acceleration fix-type 3d-precision

[data]
"""
    try:
        with open(output_file, "x") as f:
            f.write(rc_metadata)
            for line in lines:
                f.write(f"{line}\n")
    except PermissionError as err:
        print(f"{err}\nSeems you don't have permissions to write to the output file")
        sys.exit(1)
    except FileExistsError as err:
        print(
            f"{err}\nOutput file already exists, won't overwrite. Remove file or use different filename"
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "sa_log_file",
        help="REQUIRED. Speedangle log filename to convert to racechrono vbo format",
    )
    parser.add_argument("-o", "--output_file", help="Output filename")
    args = parser.parse_args()
    input_file = args.sa_log_file
    if not args.output_file:
        file_ts = str(time.time()).split(".")[0]
        output_file = f"{input_file}_{file_ts}.vbo"
    else:
        output_file = args.output_file

    timestamp, sa_lines = read_speedangle_file(input_file)
    write_racechrono_file(
        speedangle_to_racechrono_vbo(timestamp, sa_lines), output_file
    )


if __name__ == "__main__":
    main()
