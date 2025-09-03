import functools
import weakref

from .helper import log
from .inspect import is_hero_method, HERO_EVENT_ATTRIBUTE


def remote_hero_method_to_str(func: callable) -> str:
    return f"{func.__self__._name}.{func.__name__}"


class Callback:
    """
    Represent a callback function.
    """

    def __init__(self, func: callable, origin: str = None):
        self.func = func
        self.origin = origin
        if is_hero_method(func):
            self.name = remote_hero_method_to_str(func)
            self.is_remote_hero = True
        else:
            self.name = repr(func)
            self.is_remote_hero = False

    def __eq__(self, other) -> bool:
        """
        Check for equality with other `Callback`.

        Args:
            other: other callback instance.

        Returns:
            bool: equality result.
        """
        if self.is_remote_hero == other.is_remote_hero:
            if self.is_remote_hero:
                # both True
                # check if names are equal
                return self.name == other.name
            # both False
            # check if callback functions are equal
            return self.func == other.func
        # one is remote and the other one is not
        return False

    def __call__(self, *args, **kwargs):
        """
        Call the callback function.
        """
        return self.func(*args, **kwargs)

    def __hash__(self):
        """
        Generate a hash value for this callback using the name in case of remote hero methods
        or the callable itself for builtins or local callables.

        Returns:
            int: calculated hash.
        """
        if self.is_remote_hero:
            return hash(self.name)
        else:
            return hash(self.func)

    def to_dict(self) -> dict:
        """
        Generate a dictionary representation of this callback.

        Returns:
            dict: dictionary with keys: name, origin, is_remote_hero and func
        """
        return {"name": self.name, "origin": self.origin, "is_remote_hero": self.is_remote_hero, "func": self.func}


class CallbackStorage:
    """
    Store all callbacks.
    """

    def __init__(self):
        self._callbacks = {}

    def __iter__(self):
        """
        Generate an iteration for this iterable.
        """
        return iter(self._callbacks.values())

    def __contains__(self, func: callable) -> bool:
        """
        Implements the `in` operation for this class.
        """
        callback = Callback(func)
        return callback.name in self._callbacks.keys()

    def append(self, func: callable, origin: str = None) -> str:
        """
        Append a given callable to the storage.

        Args:
            func: `callable` to append.
            origin: `str` (default: `None`) indicating the origin of the callback.

        Returns:
            str: name of the callback.
        """
        callback = Callback(func, origin)
        self._callbacks[callback.name] = callback
        return callback.name

    def remove(self, func: callable) -> bool:
        """
        Remove a callable from storage.

        Args:
            func: `callable` to remove.

        Returns:
            bool: truth value indicating if the callable was a callback.
        """
        if func in self:
            callback = Callback(func)
            del self._callbacks[callback.name]
            return True
        return False

    def is_callback(self, func: callable) -> bool:
        """
        Check if given `callable` is a callback.

        Args:
            func: `callable` to check.

        Returns:
            bool: `callable` is a callback
        """
        return func in self

    def get_callbacks(self) -> list:
        """
        Get a list of all callbacks dictionaries.

        Returns:
            list: dictionary representation of all callbacks
        """
        return [cb.to_dict() for name, cb in self._callbacks.items()]


class EventHandler:
    """
    Base class for event handlers.
    """

    def connect(self, callback: callable):
        """Connect a callback function."""
        raise NotImplementedError

    def disconnect(self, callback: callable):
        """Disconnect a callback function."""
        raise NotImplementedError

    def is_callback(self, func: callable) -> bool:
        """Check if `func` is a callback"""
        raise NotImplementedError

    def get_callbacks(self):
        """Return all callbacks"""
        raise NotImplementedError


class LocalEventHandler(EventHandler):
    """
    Handles event connections for a specific instance.
    """

    def __init__(self, instance, func):
        self.instance = weakref.ref(instance)
        self.func = func
        # store callbacks for this instance
        self.callbacks = CallbackStorage()
        # mark as an hero event
        setattr(self, HERO_EVENT_ATTRIBUTE, True)
        # preserve signature and metadata of `func`
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        """
        Call the original function and trigger callbacks.
        """
        # call the method
        if self.instance() is not None:
            result = self.func(self.instance(), *args, **kwargs)
            # publish result (triggers RemoteEvent callbacks)
            endpoint = f"{self.instance()._endpoint_base_path}/{self.func.__name__}"
            self.instance()._session.put(endpoint, self.instance()._serialize(result))
            # execute callbacks
            for callback in self.callbacks:
                callback(result)
            return result
        else:
            log.error("Lost weak reference to instance for event.")
            return None

    def connect(self, callback: callable, origin: str = None) -> str:
        """
        Connect a callback function to be triggered when the method is called.

        Args:
            callback: `callable` to connect.
            origin: (optional) `str` indicting origin of this callback.

        Returns:
            str: name of the callback.
        """
        callback_name = self.callbacks.append(callback, origin)
        log.debug(
            f"{self.__class__} connecting LocalEvent callback {self.__name__} -> {callback_name} (origin: {origin})"
        )
        return callback_name

    def disconnect(self, callback: callable) -> bool:
        """
        Disconnect a callback function.

        Args:
            callback: `callable` to disconnect.

        Returns:
            bool: truth value indicating if the callable was a callback.
        """
        log.debug(f"{self.__class__} disconnecting LocalEvent callback {self.__name__} -> {callback}")
        return self.callbacks.remove(callback)

    def is_callback(self, func: callable) -> bool:
        """
        Check if given callable is already a registered callback.

        Args:
            callback: `callable` to check.

        Returns:
            bool: truth value indicating if the callable is a callback.
        """
        if is_hero_method(func):
            return remote_hero_method_to_str(func) in self.remote_hero_callbacks.keys()
        else:
            return func in self.callbacks

    def get_callbacks(self) -> list:
        """
        Return a list of registered callback functions.

        Returns:
            list: dictionary representation of all callbacks
        """
        return [{**cb, "context": "LocalHERO"} for cb in self.callbacks.get_callbacks()]


class RemoteEventHandler(EventHandler):
    """
    Handles remote events for a specific instance.
    """

    def __init__(self, instance, func: callable = None):
        self.instance = instance
        # store callbacks for this instance
        self.callbacks = CallbackStorage()
        # mark as an hero event
        setattr(self, HERO_EVENT_ATTRIBUTE, True)

    def __call__(self, payload):
        """
        Call the original function and trigger callbacks.
        """
        for callback in self.callbacks:
            callback(payload)

    def connect(self, callback: callable) -> str:
        """
        Connect a callback function to be triggered when the method is called.

        Args:
            callback: `callable` to connect.
            origin: (optional) `str` indicting origin of this callback.

        Returns:
            str: name of the callback.
        """
        if is_hero_method(callback):
            callback_name = self.instance._connect_local_hero_callback(
                event=self, remote_hero_method=callback, origin=self.instance._name
            )
            log.debug(f"{self.__class__} connecting LocalEvent callback {self.__name__} -> {callback}")
        elif callback not in self.callbacks:
            callback_name = self.callbacks.append(callback)
            log.debug(f"{self.__class__} connecting RemoteEvent callback {self.__name__} -> {callback}")
        return callback_name

    def disconnect(self, callback: callable) -> None:
        """
        Disconnect a callback function.

        Args:
            callback: `callable` to disconnect.

        Returns:
            bool: truth value indicating if the callable was a callback.
        """
        if is_hero_method(callback):
            log.debug(f"{self.__class__} disconnecting LocalEvent callback {self.__name__} -> {callback}")
            return self.instance._disconnect_local_hero_callback(event=self, remote_hero_method=callback)
        if callback in self.callbacks:
            log.debug(f"{self.__class__} disconnecting RemoteEvent callback {self.__name__} -> {callback}")
            return self.callbacks.remove(callback)

    def is_callback(self, func: callable) -> bool:
        """
        Check if given callable is already a registered callback.

        Args:
            callback: `callable` to check.

        Returns:
            bool: truth value indicating if the callable is a callback.
        """
        return func in self.callbacks

    def get_callbacks(self) -> list:
        """
        Return a list of registered callback functions.

        Returns:
            list: dictionary representation of all callbacks
        """
        remote_event_cbs = [{**cb, "context": "RemoteHERO"} for cb in self.callbacks.get_callbacks()]
        local_event_cbs = [{**cb, "context": "LocalHERO"} for cb in self.instance._get_local_hero_callbacks(event=self)]
        return [*remote_event_cbs, *local_event_cbs]


class EventDescriptor:
    """
    A descriptor to handle instance-specific event connections.
    """

    def __init__(self, func: callable = None):
        # store the original function
        self.func = func
        # store callbacks for each instance
        self._instances = weakref.WeakKeyDictionary()

    @staticmethod
    def _get_event_handler_cls():
        raise NotImplementedError

    def __get__(self, instance, owner):
        """
        Ensure the method and event-handling functions are bound to the instance.

        Args:
            self: the EventDescriptor instance
            instance: the owning `LocalHERO`/`RemoteHERO`.
            owner:
        """
        if instance is None:
            # return descriptor itself if accessed via the class
            return self
        # create an event handler for this instance if not already created
        if instance not in self._instances:
            self._instances[instance] = self._get_event_handler_cls()(instance, self.func)
        # return the instance-bound event handler
        return self._instances[instance]


class LocalEventDescriptor(EventDescriptor):
    """
    Descriptor of `@event` decorated methods of a `LocalHERO`.
    """

    @staticmethod
    def _get_event_handler_cls():
        return LocalEventHandler


class RemoteEventDescriptor(EventDescriptor):
    """
    Descriptor of remote representations of events in a `RemoteHERO`.
    """

    @staticmethod
    def _get_event_handler_cls():
        return RemoteEventHandler


def event(func: callable):
    """
    Decorator for events.

    Note:
        Only use on methods bound to objects.
    """
    return LocalEventDescriptor(func)
