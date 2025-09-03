import cbor2
import numpy as np
import weakref

from heros.helper import full_classname
from .inspect import is_hero_event, is_hero_method

ndarray_tag = 4242
hero_tag = 9000
unserializable_tag = 9001
unserializable_object_reference_tag = 9002
hero_event_tag = 9003
hero_method_tag = 9004


def is_builtin_class_instance(obj):
    return obj.__class__.__module__ == "__builtin__"


class ObjectStore:
    """
    An object store to be used to keep week references to objects identified by a serializable identifier (int64).
    """

    _cache = {}

    def add(self, object: object) -> int:
        """
        Add object to store and return it's identifier

        Args:
            object: object to store

        Returns:
            Identifier to retrieve the object from the store again
        """
        identifier = id(object)
        self._cache[identifier] = weakref.ref(object)
        return identifier

    def get(self, identifier: int) -> object:
        """
        Retrieve an object identified by :param:identifier from the store.
        If the object does not exist any more, None is returned.

        Args:
            identifier: the identifier obtained when storing the object

        Returns:
            object corresponding to the identifier or None if the object does not exist any more
        """
        if identifier not in self._cache:
            return None

        obj = self._cache[identifier]

        if obj() is not None:
            return obj()
        else:
            del self._cache[identifier]
            return None


obj_store = ObjectStore()


class UnserializableRemoteObject:
    def __init__(self, type: str, id: int, representation: str):
        self.type = type
        self.representation = representation
        self.id = id

    def __str__(self):
        return f"Unserializable Remote Object ({self.type}): id {hex(self.id)}"

    def __repr__(self):
        return self.__str__()


def cbor_default_encoder(encoder, value):
    """
    Handle custom types in serialization.
    """
    from heros import LocalHERO, RemoteHERO

    global obj_store

    if type(value) is np.ndarray:
        # encode ndarray
        encoder.encode(cbor2.CBORTag(ndarray_tag, [value.shape, str(value.dtype).encode(), value.tobytes()]))

    elif (type(value) is np.int32) or (type(value) is np.int64):
        encoder.encode(int(value))

    elif isinstance(value, LocalHERO) or isinstance(value, RemoteHERO):
        # encode a HERO
        encoder.encode(cbor2.CBORTag(hero_tag, [value._realm, value._name]))

    elif is_hero_event(value):
        # encode an event of a remote hero
        # value.instance corresponds is the HERO instance
        encoder.encode(cbor2.CBORTag(hero_event_tag, [value.instance, value.__name__]))

    elif is_hero_method(value):
        # encode a method of a remote hero
        # value.__self__ corresponds is the HERO instance
        encoder.encode(cbor2.CBORTag(hero_method_tag, [value.__self__, value.__name__]))

    elif type(value) is UnserializableRemoteObject:
        # encode an reference on an remote object that cannot be serialized
        encoder.encode(cbor2.CBORTag(unserializable_object_reference_tag, value.id))

    else:
        # for all object we cannot serialized, we hand out reference
        identifier = obj_store.add(value)
        encoder.encode(cbor2.CBORTag(unserializable_tag, [full_classname(value), identifier, str(value)]))


def cbor_tag_hook(decoder, tag, shareable_index=None):
    from heros import RemoteHERO

    global obj_store

    if tag.tag == ndarray_tag:
        # decode ndarray
        shape, dtype, buffer = tag.value
        return np.frombuffer(buffer, dtype=dtype).reshape(shape)

    if tag.tag == hero_tag:
        # decode a remote HERO
        realm, name = tag.value
        return RemoteHERO(name, realm=realm)

    if tag.tag == hero_event_tag:
        # decode a remote HERO event
        remote_hero, event_name = tag.value
        return getattr(remote_hero, event_name)

    if tag.tag == hero_method_tag:
        # decode a remote HERO method
        remote_hero, method_name = tag.value
        return getattr(remote_hero, method_name)

    if tag.tag == unserializable_tag:
        # decode
        t, i, s = tag.value
        return UnserializableRemoteObject(t, i, s)

    if tag.tag == unserializable_object_reference_tag:
        obj = obj_store.get(tag.value)
        return obj

    return tag


def serialize(obj):
    return cbor2.dumps(obj, default=cbor_default_encoder)


def deserialize(bytes):
    return cbor2.loads(bytes, tag_hook=cbor_tag_hook)
