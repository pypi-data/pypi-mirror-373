Paradigms
#########

Realms
------

To isolate groups of HERO objects from other groups the concept of realms exists in HEROS.
You can think of it as a namespace where objects in the same namespace can talk to each other while communication across realms/namespaces is
not easily possible.
Note that this is solely a management feature, not a security feature.
All realms share the same zenoh network and can thus talk to each other on this level.

Objects
-------

An object that should be shared via HEROS must inherit from the class ``LocalHero``.
When python instantiates such an object, it will parse the methods, class attributes, and :doc:`events <events>` (see event decorator) and automatically generate a list of capabilities that describes this HEROS object.
The capabilities are announced and a liveliness token for the object is created. ``HEROSOberserver`` in the network will thus be notified that our new object joined the realm.

When the object is destroyed or the link gets lost, the liveliness token disappears and any remote object will notice this.

Capabilities
------------

A HEROS object is characterized by the capabilities it provides. There are currently three types of capabilities:

* Attribute
* Method
* Event


Datasource
----------

A frequent use case for HERO is that of making data (like sensor data or status data) available to interested peers.
To cover this use case, a special class of HERO exists, the ``DatasourceHERO``. It provides a special event ``new_data`` that is always emitted when new data is available. RemoteHEROs connect to the emitting HERO will get noticed directly and react accordingly.
In addition also a ``DatasourceObsever`` class exist, that efficiently monitors the events of many HEROs in the network without fully instantiating the RemoteHEROs.
