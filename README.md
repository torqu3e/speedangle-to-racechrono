# Speedangle to Racechrono
## Speedangle .sa to racechrono .vbo converter

This script lets you use a .sa file as exported from a Speedangle apex lap timer using the R4 software and convert it into a .vbo file that racechrono accepts natively.

There are no dependencies for this script except there needs to be python3 installed. I made sure to use the inbuilt math library instead of numpy to facilitate this as well.

If you run into any issues using this script please report the problem so I can try to address it. 

## Usage

```
python3 speedangle_2_racechrono.py ~/Downloads/BARBER\ 110820\ 140040.sa -o barber.vbo
```
* After the conversion, send the .vbo file to the phone/tablet device using whatever medium works for you (email, gdrive etc.)
* In racechrono, click import from the three dot menu in top right, select data type as RaceHF/VBOX Sport, click file browser and point to the newly uploaded vbo file.
* Click Start

If successfully imported you should have the session available in the UI.

```
$ python3 speedangle_2_racechrono.py -h
usage: speedangle_2_racechrono.py [-h] [-o OUTPUT_FILE] sa_log_file

positional arguments:
  sa_log_file           REQUIRED. Speedangle log filename to convert to racechrono vbo format

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Output filename
```

## Screenshots 

![Analysis screen - Barber] (barber_analysis.jpeg)
![Corner speeds - Grattan] (grattan_speeds.jpeg)
