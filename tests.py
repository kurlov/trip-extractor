from file_handler import FileHandler
from processor import ListProcessor


def test_list_one_trip():
    file_IO = FileHandler()
    ws = file_IO.read_waypoints('data/test/waypoints.json')
    list_proc = ListProcessor(ws)
    trips = list_proc.get_trips()
    assert len(trips) == 1
