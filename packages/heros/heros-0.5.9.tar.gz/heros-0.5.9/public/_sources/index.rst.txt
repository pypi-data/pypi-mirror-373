.. HEROS documentation master file, created by
   sphinx-quickstart on Fri Jan 17 13:05:36 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

HEROS - Highly Efficient Remote Object Service
===============================================

HEROS is a decentralized object sharing service. In simple words it makes your software objects network transparent.
To be fast and efficient, HEROS relies on eclipse-zenoh as a transport layer.
It thus supports different network topologies and hardware transports.
Most notably, it can run completely decentralized, avoiding a single point of failure and at the same time guaranteeing low latency and and high bandwidth communication through p2p connections.

HEROS provides a logical representation of software objects and is not tied to any specific language.
Even non-object oriented programming languages might provide a collection of functions, variables, and events to be accessible as an object in HEROS.

Very much like a Dynamic Invocation Infrastructure (DII) in  a Common Object Broker Architecture (CORBA), HEROS handles objects dynamically during runtime rather than during compile time.
While this does not allow to map HEROS objects to be mapped to the language objects in compiled languages, languages supporting monkey-patching (python, js, ...) are still able to create proxy objects during runtime.

The working principle is shown in the following.

.. image:: _static/principle.svg
  :width: 400
  :alt: working principle of HEROS


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   paradigms
   installation
   usage
   events
   metadata
   faq
