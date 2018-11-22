from file_handler import FileHandler
from processor import ListProcessor

file_IO = FileHandler()
waypoints = file_IO.read_waypoints('data/waypoints.json')
list_proc = ListProcessor(waypoints)
trips = list_proc.get_trips()
file_IO.save_trips(trips)