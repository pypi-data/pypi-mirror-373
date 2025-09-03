from heros import PolledLocalDatasourceHERO

import random
import argparse

import asyncio

random.seed()


class TestObject(PolledLocalDatasourceHERO):
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

    def _new_data(self):
        self.testme += 1
        return {"foo": (self.testme, "mW"), "bar": self.foovar}


parser = argparse.ArgumentParser(prog="remote_object", description="Example of how to access a remote HERO")
parser.add_argument("--realm", "-r", default="heros", type=str)
parser.add_argument("name", help="identifier of the remote HERO")
args = parser.parse_args()

loop = asyncio.new_event_loop()

observables = {
    "foo": {"conversion": "exp(0.32*x-15.3)"},
    "nonexistent": {},
    "bar": {"unit": "MOhm", "boundaries": [[18, 26], [14, 30]]},
}

obj = TestObject(args.name, loop=loop, realm=args.realm, observables=observables)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    obj.close()
