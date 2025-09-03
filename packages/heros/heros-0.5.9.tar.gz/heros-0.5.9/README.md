# HEROS - Highly Efficienct Remote Object Service


![heros logo](docs/_static/heros_logo.svg)
![heros logo](docs/_static/heros_text.svg)


HEROS is a decentralized object sharing service. In simple words it makes your software objects network transparent.
To be fast and efficient, HEROS relies on the minimal overhead eclipse-zenoh protocol as a transport layer. It thus
supports different network topologies and hardware transports. Most notably, it can run completely decentralized,
avoiding a single point of failure and at the same time guaranteeing low latency and and high bandwidth communication
through p2p connections.

HEROS provides a logical representation of software objects and is not tied to any specific language. Even non-object
oriented programming languages might provide a collection of functions, variables, and events to be accessible as an
object in HEROS.

Very much like a Dynamic Invocation Infrastructure (DII) in  a Common Object Broker Architecture (CORBA), HEROS handles
objects dynamically during runtime rather than during compile time. While this does not allow to map HEROS objects to
be mapped to the language objects in compiled languages, languages supporting monkey-patching (python, js, ...) are
still able create proxy objects during runtime.

Find the HEROS documentation under [https://atomiq-project.gitlab.io/heros](https://atomiq-project.gitlab.io/heros)

## Paradigms

### Realms
To isolate groups of HEROs from other groups, the concept of realms exists in HEROS. You can think of it as a
namespace where objects in the same namespace can talk to each other while communication across realms/namespaces is
not easily possible. Note that this is solely a management feature, not a security feature. All realms share the same
zenoh network and can thus talk to each other on this level.

### Objects
An object that should be shared via HEROS must inherit from the class `LocalHero`. When python instantiates such
an object, it will parse the methods, class attributes, and events (see event decorator) and automatically generate
a list of capabilities that describes this HEROS object. The capabilities are announced and a liveliness token for the
object is created. HEROSOberserver in the network will thus be notified that our new object joined the realm.

When the object is destroyed or the link gets lost, the liveliness token disappears and any remote object will notice
this.

### Capabilities
A HEROS object is characterized by the capabilities it provides. There are currently three types of capabilities:

 * Attribute
 * Method
 * Event


### Metadata
A HERO can carry metadata that allows for easier classification in environments with many HEROs. In addition to a list of tags, the metadata can also carry information on what interfaces a HERO provides. This allow a HERO to signal that it can seamlessly be used as an object of a certain class.
