Usage
#####

Building your first HERO is very simple. Just write your custom class and make it inherit from ``heros.LocalHero``.

A simple example can be seen

.. literalinclude:: ../../examples/share_local_hero_simple.py
   :language: python

Due to the infinite loop, the script will not terminate and keep the object ``obj`` alive. Since it inherits from ``heros.LocalHERO``, the object was analyzed upon instantiation and provided as a HERO to the network.
This means, we can now simply access the method attributes of the object from a remote site.

To get remote access we can run the following in a different process or on a different machine in the same network (UDP broadcast needs to reach the other machine for discovery):

.. literalinclude:: ../../examples/access_remote_hero_simple.py
    :language: python

Nested HEROs
------------

HEROS is able to serialize HEROs as references to a HERO.
This allows to pass a HERO between the local and the remote site.
When either of the sites receives such a reference, it creates a ``RemoteHERO`` to access the referenced HERO.
This allows things like

 1. Deep access to HEROs nested inside of HEROs.
 2. Passing HEROs as arguments into methods exposed by a HERO.
 3. Retrieving HEROs returned by a HERO.


Unserializable Objects
----------------------

A HERO attribute or method might return an object that is not a HERO and can not be serialized.
In that case, the returned object is cached on the side of the ``LocalHERO`` and an identifier is sent to the remote side. The remote side can store the reference locally.
If the reference is sent back to the ``LocalHERO`` side, the corresponding object is taken from the cache and inserted into the request instead of the reference.
This allows to instruct the LocalHERO to do something with an object that cannot be transferred.
This allows, for example, to hand over an unserializable object retrieved earlier as argument to a function.

.. note::
   The cache that keeps the object references uses only weak references to to avoid memory leaks.
   That means that an object can be garbage collected if not any other instance keeps a reference on it.
