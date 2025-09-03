HERO Metadata
####################

.. _sec-events:

Metadata
--------

If your HERO network grows larger, managing the large number of HEROs becomes tedious. It is then necessary To
classify your HEROs somehow. This is why a HERO carries metadata in it's discovery information. This metadata is

* The identifier/name of the HERO
* The class it was created from
* An optional list of interfaces it implements
* An optional list of tags attached to the HERO


The information of a LocalHERO that is controlling an RF device could look like the following

.. code-block:: json

    {
        "name": "my_rfdevice",
        "class": "vendorlibrary.module.rfdevice_class"
        "implements": ["atomiq.components.electronics.rfsource.RFSource"],
        "tags": ["boss:27ea419fe", "raspberry", "datasource"]
    }

In this case the HERO signals that it implements an `atomiq RFSource <https://atomiq-project.gitlab.io/atomiq/components/electronics/rfsource/RFSource.html>`_,
it was started by `BOSS <https://gitlab.com/atomiq-project/boss>`_ under a particular ID, it runs on a Raspberry Pi and is a datasource.

While the value for `class` is automatically determined from the class the LocalHERO has, setting values for the `name`, `implements`, and `tags` fields is up to the user.
All three fields can be set through the constructor of the LocalHERO class. Additionally, `implements`, and `tags` can be set through class level
attributes in your custom class that inherits from LocalHERO like shown in the following:

.. code-block:: python

    from heros import LocalHERO


    class DummyRFDevice(LocalHERO):
        _hero_implements = ["atomiq.components.electronics.rfsource.RFSource"]
        _hero_tags = ["raspberry", "datasource"]

        def my_method(self):
            pass

    ...

.. note::
    If values are given in the constructor and at class level, the lists are joined and converted to a list to avoid duplicates.

In a RemoteHERO the metadata is available from the class level attributes that could also be used on the LocalHERO side:

.. code-block:: python

    In [1]: from heros import RemoteHERO

    In [2]: obj = RemoteHERO("my_rfdevice")

    In [3]: obj._hero_implements
    Out[3]: {'atomiq.components.electronics.rfsource.RFSource'}

    In [4]: obj._hero_tags
    Out[4]: {'raspberry', 'datasource'}

.. note::
    Since the metadata is part of the discovery endpoint, it is also available in a HEROObserver.