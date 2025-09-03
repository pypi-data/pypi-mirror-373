import time

from heros.datasource import DatasourceObserver

obs = DatasourceObserver("*")


def printer(obj_name, data):
    print(f"got message from {obj_name}: {data}")


obs.register_new_data_callback(printer)

while True:
    time.sleep(1)
