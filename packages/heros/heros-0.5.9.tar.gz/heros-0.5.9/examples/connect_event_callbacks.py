from heros import LocalHERO, event, RemoteHERO, log

import asyncio

log.setLevel("DEBUG")


class Alice(LocalHERO):
    testme: int = 0

    def print_from_afar(self, payload) -> str:
        print(f"printed from {self._name} {payload}")

    def hello(self) -> str:
        self.testme += 1
        return "world"

    @event
    def new_data(self, value):
        return value


class Bob(Alice):
    pass


# Create two local objects and two remote representations of them.
alice = Alice("alice")
bob = Bob("bob")

remote_alice = RemoteHERO("alice")
remote_bob = RemoteHERO("bob")

# When connecting these objects with events and callbacks, we can distinguish 4 cases:
alice.new_data.connect(print)  # case A: local object, local callback
alice.new_data.connect(remote_bob.print_from_afar)  # case B: local object, remote callback

remote_alice.new_data.connect(print)  # case C: remote object, local callback
remote_alice.new_data.connect(remote_bob.print_from_afar)  # case D: remote object, remote callback (p2p dispatch)

# Print the connected callbacks for all objects
for o in [alice, remote_alice]:
    print(f"Connected callbacks for {o}:")
    print(o.new_data.get_callbacks())
    print("###")

# Now remove the all callbacks from remote_alice which are called from remote_alice
for cb in remote_alice.new_data.get_callbacks():
    if cb["context"] == "RemoteHERO":
        print(f"Removing {cb['name']} from remote_alice.new_data")
        remote_alice.new_data.disconnect(cb["func"])
print("###")
print("Remaining callbacks to remote_alice.new_data")
print(remote_alice.new_data.get_callbacks())
print("###")


# Emit data from the from events
loop = asyncio.new_event_loop()


async def emit_data():
    i = 0
    while True:
        alice.new_data(["Alice", i])
        bob.new_data(["Bob", i])
        i += 1
        await asyncio.sleep(1)


# Keep running
loop.create_task(emit_data())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
