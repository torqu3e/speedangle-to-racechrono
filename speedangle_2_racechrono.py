"""
Description: Speedangle .sa to Racechrono .vbo format converter
Author: Tejinder Singh
Version : v0.0.2

Changes:
* Added heading calculated from coordinate delta
* Fixed longitude inversion
* Lean angle data requires additional channel for vbo import to RC. TB fixed by @aol

TBD:
* Figure heading calculation borked for some tracks
* Get Racechrono to .sa file import in the app

Reference:
SA log format definition on last 2 pages - http://www.speedangle.com/sauploads/2020/12/SpeedAngle-R4-APEX-R011-User-Manual-2020-0412.pdf
Converting to vbo coordinates - https://racelogic.support/01VBOX_Automotive/01General_Information/Knowledge_Base/VBOX_Latitude_and_Longitude_Calculations
VBO file format (not 100% accurate for RaceChrono) - https://racelogic.support/01VBOX_Automotive/01General_Information/Knowledge_Base/VBO_file_format#:~:text=VBOX%20data%20files%20are%20saved,as%20word%20processors%20or%20spreadsheets.&text=The%20%5Bcolumn%20names%5D%20parameter%20specifies,column%20of%20the%20data%20section.
"""


#!/usr/bin/env python3
import argparse
import datetime
import logging
from math import cos, sin, atan2, degrees
import re
import sys
import time
from lap_analysis import analyze

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(asctime)s %(message)s")


def read_speedangle_file(input_file):
    ts_pattern = re.compile("^#D=.*")
    log_pattern = re.compile(
        "-?[0-9]{1,3}.[0-9]{6},-?[0-9]{1,3}.[0-9]{6},(-?[0-9]{1,3},){8}[F0-9]"
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
        logging.error(f"{err}\nCheck input filename")
        sys.exit(1)
    except PermissionError as err:
        logging.error(f"{err}\nSeems you don't have permissions to read the input file")
        sys.exit(1)
    logging.info(f"Read speedangle source file {input_file}")
    return log_timestamp, lines


def speedangle_to_racechrono_vbo(timestamp: str, sa_lines: list, analyze: bool):
    rc_lines = []
    p_lat = p_lon = 0.0
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
        sector = str(v[-1])
        hed = calc_heading(lat, lon, p_lat, p_lon)
        sat = int(v[8])
        if not analyze:
            rc_lines.append(
                f"{sat:03} {line_time:6.2f} {lat*60:5.6f} {-lon*60:5.6f} {vel:3.2f} {hed:3.2f} 00000.00 {accl:3.3f} 000.000 0000000.000 +010.000 {ang:3.3f} {accl:3.3f} 3 02.46"
            )
        else:
            rc_lines.append(
                f"{line_time:6.2f} {lat:5.6f} {lon:5.6f} {vel:3.2f} {hed:3.2f} {accl:3.3f} {ang:3.3f} {accl:3.3f} {sector}"
            )
        p_lat, p_lon = lat, lon
    logging.info("Format conversion complete")
    return rc_lines


def calc_heading(lat: float, lon: float, p_lat: float, p_lon: float) -> float:
    delta = lon - p_lon
    x = cos(lat) * sin(delta)
    y = cos(p_lat) * sin(lat) - sin(p_lat) * cos(lat) * cos(delta)
    return degrees(atan2(x, y))


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
        logging.info(f"Wrote racechrono .vbo file {output_file}")
    except PermissionError as err:
        logging.error(
            f"{err}\nSeems you don't have permissions to write to the output file"
        )
        sys.exit(1)
    except FileExistsError as err:
        logging.error(
            f"{err}\nOutput file already exists, won't overwrite. Use different filename or don't provide one to autogenerate"
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--in_file",
        help="Required - .sa input filename",
    )
    parser.add_argument("-o", "--out_file", help=".vbo output filename")
    parser.add_argument(
        "-a", "--analyze", action="store_const", const=True, help="Analyze only"
    )

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()

    if args.in_file:
        timestamp, sa_lines = read_speedangle_file(args.in_file)

        if not args.out_file:
            file_ts = str(time.time()).split(".")[0]
            output_file = f"{args.in_file}_{file_ts}.vbo"
        else:
            output_file = args.out_file

        if args.analyze:
            analyze(speedangle_to_racechrono_vbo(timestamp, sa_lines, args.analyze))
        else:
            write_racechrono_file(
                speedangle_to_racechrono_vbo(timestamp, sa_lines, args.analyze),
                output_file,
            )


if __name__ == "__main__":
    main()
