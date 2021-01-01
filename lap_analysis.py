from datetime import datetime
import json


class laps:
    def __init__(self, num, start, end):
        self.num = num
        self.start = start
        self.end = end
        self.sectors = []
        self._lap_time = 0.0

    @property
    def lap_time(self):
        lt = (self.end - self.start).total_seconds()
        if lt > 0:
            return lt
        else:
            return 0.0

    def __repr__(self):
        return f"{self.stats()}"

    def stats(self):
        start = datetime.strftime(self.start, "%H:%M:%S.%f").replace("00000", "")
        end = datetime.strftime(self.end, "%H:%M:%S.%f").replace("00000", "")
        lap_stats = dict(
            lap_number=self.num,
            lap_start=start,
            lap_end=end,
            lap_time=self.lap_time,
            sectors=[
                datetime.strftime(x, "%H:%M:%S.%f").replace("00000", "")
                for x in self.sectors
            ],
        )
        return lap_stats


def analyze(raw_data: list):
    lap_list = []
    lap_counter = 0
    for item in raw_data:
        line = item.split()
        if line[-1] == "F":
            lap_counter += 1
            start = datetime.strptime(line[0], "%H%M%S.%f")
            end = datetime.strptime("000.0", "%H%M%S.%f")
            lap = laps(lap_counter, start, end)
            lap_list.append(lap)
            if lap_counter > 1:
                lap_list[lap_counter - 2].end = start
        elif int(line[-1]) > 0:
            lap.sectors.append(datetime.strptime(line[0], "%H%M%S.%f"))
    for _ in lap_list:
        print(json.dumps(_.stats()))
