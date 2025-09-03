from heros import LocalHERO, event

import random
import time
import argparse

random.seed()


class TestObject(LocalHERO):
    _hero_implements = ["atomiq.components.electronics.dac.DAC"]
    _hero_tags = ["microhero", "bossed"]

    foovar: str = ""
    testme: int = 0

    def read_temp(self, min: int, max: int) -> float:
        result = random.randint(min, max)
        print(f"returning result {result}")
        print(f"btw, foovar is {self.foovar}")
        return result

    def hello(self) -> str:
        self.testme += 1
        return "world"

    @event
    def new_data(self, value):
        return value


parser = argparse.ArgumentParser(prog="remote_object", description="Example of how to access a remote HERO")
parser.add_argument("--realm", "-r", default="heros", type=str)
parser.add_argument("name", help="identifier of the remote HERO")
args = parser.parse_args()

with TestObject(args.name, realm=args.realm) as obj:
    # keep running
    i = 0
    while True:
        time.sleep(1)
        obj.new_data({"test_data": (i, "mV")})
        i += 1
