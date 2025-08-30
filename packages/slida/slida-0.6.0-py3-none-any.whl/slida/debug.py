import datetime
from time import time


live_objects: dict[int, tuple[str, float]] = {}


def add_live_object(obj_id: int, obj_name: str):
    live_objects[obj_id] = obj_name, time()


def remove_live_object(obj_id: int):
    try:
        live_objects.pop(obj_id)
    except KeyError:
        pass


def print_live_objects():
    print("LIVE OBJECTS:")
    for obj_id, (obj_name, timestamp) in sorted(live_objects.items(), key=lambda i: i[1][1]):
        print(f"{hex(obj_id)} \t {obj_name} \t {datetime.datetime.fromtimestamp(timestamp)}")
