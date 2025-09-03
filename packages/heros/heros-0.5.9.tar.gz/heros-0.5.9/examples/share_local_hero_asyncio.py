from heros import LocalHERO, event

import random
import argparse

import asyncio

random.seed()


class TestObject(LocalHERO):
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

obj = TestObject(args.name, realm=args.realm)

loop = asyncio.new_event_loop()


async def emit_data():
    i = 0
    while True:
        obj.new_data(["test_data", i])
        i += 1
        await asyncio.sleep(1)


loop.create_task(emit_data())

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    obj.close()
