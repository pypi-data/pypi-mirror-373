FAQ
###

Can I use private methods and attributes?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, private methods and attributes (name starting with a :code:`_`) are not exposed to the remote side.

However, you can force private methods to be exposed by decorating them with :code:`@heros.inspect.force_remote`.

For attributes there is currently no straight forward way to force this.


Can I use Heros with ARTIQ without using Atomiq?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes, **even if we do not recommend it an there is no real point in it other than for a temporary transitionary setup!**
Just install HEROS within your `flake.nix` (adapt the version to the latest):

.. code-block:: nix

    heros = pkgs.python3Packages.buildPythonPackage rec {
      name = "heros";
      pname = "heros";
      format = "pyproject";
      version = "0.5.0";
      nativeBuildInputs = [
        pkgs.autoPatchelfHook
        ];
      src = pkgs.python3Packages.fetchPypi {
        inherit pname version;
        sha256 = "lXvd8N1BnHRWidwESy42ZlRopEX/y/uLXv+NCnxPWwo=";
      };
      buildInputs = [ pkgs.python3Packages.cbor2 pkgs.python3Packages.hatchling pkgs.python3Packages.numpy pkgs.python3Packages.zenoh];
    };


and add :code:`heros` to the python packages loaded on shell creation.

.. note::

   If you are using Atomiq, this is all handled automatically and you can just add your HERO
   `to the components DB <https://atomiq-atomiq-project-515d34b8ff1a5c74fcf04862421f6d74a00d9de1b.gitlab.io/heros.html>`_ with the :code:`$` identifier.

To use a remote hero as a device in the device DB, you have to circumvent the device manager to be passed to the :code:`RemoteHERO` class
by creating a device like:

.. code-block:: python

  class ArtiqRemoteHERO(RemoteHERO)
    def __new__(cls, dmgr, name: str, realm: str = "heros", *args, **kwargs):
        return RemoteHERO.__new__(cls, name,realm, *args, **kwargs)

    def __init__(self, dmgr,  name: str, realm: str="heros", *args, **kwargs):
        super().__init__(name, realm, *args, **kwargs)

and adding it to the device db:

.. code-block:: python

   device_db["my_hero"] = {
      "type": "local",
      "module": "my.lib",
      "class":"ArtiqRemoteHERO",
      "arguments": {
          "name":"my_remote_hero"
          }
   }
