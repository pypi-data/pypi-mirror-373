Events and Callbacks
####################

.. _sec-events:

Events
------
Methods of custom classes inheriting from ``LocalHERO`` can be marked as an event using the ``@event`` decorator.
Doing so replaces the method with a ``heros.event.LocalEventHandler`` and implies two things:

 1. The method now supports callbacks (see :ref:`sec-callbacks`) which are executed using the return value of the decorated method.
 2. The return value of the decorated method is published to a unique endpoint within the realm of the zenoh network.

In the remote representation of the object - the ``RemoteHERO`` - the event is represented as a ``heros.event.RemoteEventHandler``.
This the remote event supports callbacks which are executed using the payload received via the local event endpoint in the zenoh network.

.. note::
    The remote representation of an event is not callable itself.


.. _sec-callbacks:

Callbacks
---------
The syntax for using callbacks is regardless whether the we deal with a local or a remote event.
Connecting or disconnecting a callable ``func`` as a callback to an event ``my_event`` is performed via ``my_event.connect(func)`` and ``my_event.disconnect(func)``, respectively.
Calling ``my_event.get_callbacks()`` returns a list of callbacks.

Callbacks of events can be categorized into four cases differentiated by the execution context of the event (``LocalEventHandler`` or ``RemoteEventHandler``) and the type of the callable.
Consider the event ``my_event`` of ``alice``:

.. code-block:: python

    class Alice(LocalHERO):
        @event
        def my_event(self, value):
            return do_sth(value)

    # instantiate a local alice
    alice = Alice()

Additionally, consider the three execution contexts (i.e. three python interpreters on three hosts):

 1. ``ALICE`` where the ``LocalHERO`` of a class ``Alice`` is instantiated.
 2. ``BOB`` where the ``LocalHERO`` of a class ``Bob`` is instantiated.
 3. ``EVE`` where only remote representations (``RemoteHERO``) of ``alice`` and ``bob`` are present.

For a full example, also consider ``examples/connect_event_callbacks.py``.


Case A: Local object, local callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # execution context ALICE
    alice.my_event.connect(print)

Whenever ``my_event`` returns, the function ``print`` is called in the execution context ``ALICE``.
Therefore, the callback can be understood as ``print(alice.my_event(value))``.


Case B: Local object, remote callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # execution context ALICE
    # get a remote representation of bob
    remote_bob = RemoteHERO("bob")
    alice.my_event.connect(remote_bob.the_builder)

Whenever ``my_event`` returns, the method ``the_builder`` of the remote representation of ``bob`` is called in the execution context ``ALICE``.
Therefore, the callback can be understood as ``remote_bob.the_builder(alice.my_event(value))``.


Case C: Remote object, local callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # execution context EVE
    # get a remote representation of alice
    remote_alice = RemoteHERO("alice")
    remote_alice.my_event.connect(print)

Whenever ``my_event`` of ``alice`` (the ``LocalHERO``) returns, the function ``print`` is called in the execution context of ``EVE``.
In this case, the ``RemoteEventHandler`` representation of the ``my_event`` (``remote_alice.my_event``) calls ``print`` once it receives the return value of ``alice.my_event`` via the zenoh network.


Case D: Remote object, remote callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # execution context EVE
    # get remote representations of alice and bob
    remote_alice = RemoteHERO("alice")
    remote_bob = RemoteHERO("bob")
    remote_alice.my_event.connect(remote_bob.the_builder)

Connecting the remote callable ``remote_bob.the_builder`` to the remote representation ``remote_alice.my_event`` in the context of ``EVE`` leads to a special behavior.
The callable ``remote_bob.the_builder`` is automatically attached as a remote callback to ``alice`` (the ``LocalHERO``) similar to case B.
This way, calling ``remote_bob.the_builder`` upon return of ``alice.my_event`` is handled as a direct P2P connection between the contexts ``ALICE`` and ``BOB``.
