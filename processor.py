from datetime import datetime
from typing import Union, NamedTuple, Tuple

from geopy import distance

GPS_DISTANCE_ACCURATE_METERS = 15
STOP_TIME_SECONDS = 180
MIN_TRIP_DISTANCE_METERS = 100
CONNECTION_LOST_TIMEOUT_SECONDS = 600
CONNECTION_LOST_DISTANCE_THRESHOLD_METERS = 1000


class Waypoint(NamedTuple):
    timestamp: datetime
    lat: float
    lng: float

    def coords(self) -> Tuple[float, float]:
        """
        Helper for getting coords

        :return: Tuple
        """
        return self.lat, self.lng


class Trip(NamedTuple):
    distance: int
    start: Waypoint
    end: Waypoint


class DrivingDetector:
    @staticmethod
    def calc_distance(first: Waypoint, second: Waypoint) -> int:
        """
        Calculates distance between two points in meters

        :param first: Waypoint
        :param second: Waypoint
        :return: int
        """
        return int(distance.vincenty(first.coords(), second.coords()).m)

    def is_driving(self, first: Waypoint, second: Waypoint) -> bool:
        """
        Detects whenever vehicle is moving or not

        :param first: Waypoint
        :param second: Waypoint
        :return: bool
        """
        dist = self.calc_distance(first, second)
        time_delta = (second.timestamp - first.timestamp).seconds
        if dist > GPS_DISTANCE_ACCURATE_METERS and time_delta < STOP_TIME_SECONDS:
            return True
        elif GPS_DISTANCE_ACCURATE_METERS < dist < CONNECTION_LOST_DISTANCE_THRESHOLD_METERS and \
                time_delta < CONNECTION_LOST_TIMEOUT_SECONDS:
            return True
        else:
            return False


class ListProcessor(DrivingDetector):
    def __init__(self, waypoints: Tuple[Waypoint]):
        """
        On initialization the ListProcessor receives the full list of all
        waypoints. This list is held in memory, so the ListProcessor has access
        to the whole list of waypoints at all time during the trip extraction
        process.
        :param waypoints: Tuple[Waypoint]
        """
        self._waypoints = waypoints

    def get_trips(self) -> Tuple[Trip]:
        """
        This function returns a list of Trips, which is derived from
        the list of waypoints, passed to the instance on initialization.
        """
        def update_current_trip(trips, finish):
            current_trip = trips.pop()
            d = self.calc_distance(current_trip.start, finish)
            t = Trip(d, current_trip.start, finish)
            trips.append(t)

        if len(self._waypoints) < 2:
            return tuple()
        trips = []
        trip_started = False
        for x in range(1, len(self._waypoints)):
            first_point = self._waypoints[x-1]
            second_point = self._waypoints[x]
            if self.is_driving(first_point, second_point):
                if not trip_started:
                    trip_started = True
                    dist = self.calc_distance(first_point, second_point)
                    trip = Trip(dist, first_point, second_point)
                    trips.append(trip)
                elif trip_started and x == len(self._waypoints)-1:
                    update_current_trip(trips, second_point)
            else:
                if trip_started:
                    update_current_trip(trips, first_point)
                    trip_started = False
        trips = [t for t in trips if t.distance > MIN_TRIP_DISTANCE_METERS]
        return tuple(trips)


class StreamProcessor(DrivingDetector):

    def __init__(self):
        self.prev_point = None
        self.start_point = None

    def process_waypoint(self, waypoint: Waypoint) -> Union[Trip, None]:
        """
        Instead of a list of Waypoints, the StreamProcessor only receives one
        Waypoint at a time. The processor does not have access to the full list
        of waypoints.
        If the stream processor recognizes a complete trip, the processor
        returns a Trip object, otherwise it returns None.
        :param waypoint: Waypoint
        """

        # ignore the first entry, just remember it for further compares
        if not self.prev_point:
            self.prev_point = waypoint
            return None

        if self.is_driving(self.prev_point, waypoint):
            if not self.start_point:
                # indicates trip start
                self.start_point = self.prev_point
        else:
            # indicates trip finish
            if self.start_point:
                d = self.calc_distance(self.start_point, self.prev_point)
                trip = Trip(d, self.start_point, self.prev_point)
                self.start_point = None
                return trip
            self.prev_point = waypoint
        return None


