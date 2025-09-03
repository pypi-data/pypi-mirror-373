import time
from heros import LocalHERO


class TestObject(LocalHERO):
    testme: int = 0

    def __init__(self, name: str, start: int, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.testme = start

    def read_temp(self, min: int, max: int) -> float:
        return (max + min) / 2

    def hello(self) -> str:
        self.testme += 1
        return "world"


with TestObject("my_hero", 5) as obj:
    # keep running with infinite loop
    while True:
        time.sleep(1)
