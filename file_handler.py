import json
from datetime import datetime
from typing import Tuple

from processor import ListProcessor, Waypoint, StreamProcessor


class FileHandler:

    def __init__(self):
        self.TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def create_point(self, timestamp: str, lat: str, lng: str) -> Waypoint:
        """
        Coverts string params into Waypoint

        :param timestamp: str
        :param lat: str
        :param lng: str
        :return: Waypoint
        """
        ts = datetime.strptime(timestamp, self.TIMESTAMP_FORMAT)
        latitude = float(lat)
        longitude = float(lng)
        return Waypoint(ts, latitude, longitude)

    def serialize_datetime(self, dt: datetime) -> str:
        """
        Helper for JSON datetime serialization

        :param dt: datetime
        :return: str
        """
        if isinstance(dt, datetime):
            return dt.strftime(self.TIMESTAMP_FORMAT)

    def read_waypoints(self, filename: str) -> Tuple[Waypoint]:
        """
        Parse waypoints from file

        For the sake of simplicity it does not have parse error handlers

        :param filename: str
        :return: Union[Waypoint, None]
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        waypoints = tuple(self.create_point(**d) for d in data)
        return waypoints

    def save_trips(self, trips, filename='data/result.json'):
        """
        Saves trips to the file

        :param trips: Tuple[Trip]
        :param filename: str
        :return:
        """
        with open(filename, 'w') as f:
            json.dump(trips, f, default=self.serialize_datetime)


if __name__ == '__main__':
    r = FileHandler()
    ws = r.read_waypoints('data/waypoints.json')
    print(len(ws))
    print(ws[0])
    p = ListProcessor(ws)
    s = StreamProcessor()
    for x in range(100):
        print(s.process_waypoint(ws[x]))
    tt = p.get_trips()
    print(len(tt))
    print(tt[0])
    print(tt[1])
    for t in tt:
        print(t.distance)
