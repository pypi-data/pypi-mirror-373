import zenoh
import traceback
import uuid
from functools import partial
from .capabilities import Capability, MethodCapability, AttributeCapability, EventCapability
from .event import RemoteEventDescriptor
from .inspect import is_hero_event, is_local_only, is_force_remote, local_only, force_remote, mark_hero_method
from heros import serdes
from heros.zenoh import session_manager as default_session_manager
from .helper import object_name_from_keyexpr, log


class HEROPeer:
    """
    A HEROPeer provides the minimal interface to establish the HERO communication on top of the zenoh backend.
    To this end, it provides methods to send cbor-serialized messages via the zenoh network. It establishes
    the `@object` namespace and communicates in a defined realm. Methods to discover objects in the realm and
    to retrieve their object information are provided.

    Args:
        realm: Name of the realm that this HEROPeer belongs to. (default: heros)
        session: optional zenoh session to use. If none is provided, a new zenoh session will be started
    """

    _ep_discover = "_discover"
    _ep_capabilities = "_capabilities"
    _ep_health = "_health"
    _ns_objects = "@object"
    _default_encoding = zenoh.Encoding.APPLICATION_CBOR

    def __init__(self, realm: str = "heros", session_manager=None):
        self._realm = realm
        self._session_manager = default_session_manager if session_manager is None else session_manager
        self._session = self._session_manager.request_session(self)
        self._subscriptions = []
        self._queryables = []

    def _query_selector(self, *args, **kwargs) -> list:
        """
        Send a query to an endpoint and deserialize the results. This is a low-level function.

        Args:
            selector: The zenoh selector.
            target: zenoh target for the query
            timeout: timeout for the zenoh get command

        Returns:
            list: list of deserialized results
        """
        if "payload" in kwargs:
            kwargs["payload"] = self._serialize(kwargs["payload"])

        replies = self._session.get(*args, **kwargs)
        results = []
        for reply in replies:
            try:
                if not reply.err:
                    log.debug(
                        f"Received ('{reply.ok.key_expr}': '{reply.ok.payload.to_bytes()}') of kind"
                        f" {reply.ok.kind} from {reply.replier_id}"
                    )
                    results.append(self._deserialize(reply.ok.payload.to_bytes()))
                else:
                    log.error(f"Received error from remote: {self._deserialize(reply.err.payload.to_bytes())}")
            except Exception as e:
                log.error(f"ERROR querying remote: {e}")
        return results

    def _subscribe_selector(self, selector: str, callback: callable, *args, **kwargs):
        """
        Subscribe to a zenoh selector and a attach a callback.
        The callback receives the deserialized payload of the messages published.

        Args:
            selector: zenoh selector for the subscription. See the zenoh documentation for valid descriptors.
            callback: method to be called for messages that match the selector. The method needs to accept one argument
                which is the deserialized payload of the message.
        """
        log.debug(f"subscribing to topic {selector} with callback {callback}")

        def _zenoh_callback_wrapper(sample, _cb=callback):
            return _cb(sample.key_expr, self._deserialize(sample.payload.to_bytes()))

        sub = self._session.declare_subscriber(selector, _zenoh_callback_wrapper, *args, **kwargs)
        self._subscriptions.append(sub)

        return sub

    def _declare_queryable(self, selector: str, callback: callable):
        q = self._session.declare_queryable(selector, callback)

        self._queryables.append(q)

        return q

    def _get_object_info(self, object_name: str, timeout: float = 10.0) -> dict:
        """
        Retrieve the object information for a HERO in the current realm and with the given name.

        Args:
            object_name: name of the HERO to get the object info for. This name is inserted into a zenoh key expression
                and can thus contain the corresponding wildcards.
            timeout: timeout for the discover operation in seconds (default: 10)

        Returns:
            dict of the form {name: {remote_object_descriptor}}
        """
        ro_descriptors = self._query_selector(
            f"{self._ns_objects}/{self._realm}/{object_name}/{self._ep_discover}",
            target=zenoh.QueryTarget.ALL,
            timeout=timeout,
        )
        return {ro_descriptor["name"]: ro_descriptor for ro_descriptor in ro_descriptors}

    def _discover(self, timeout: float = 10.0) -> dict:
        """
        Send query to discovery endpoint of all HEROs in the current realm.
        All alive objects will respond and send their remote object descriptor.

        Args:
            timeout: timeout for the discover operation in seconds (default: 10)

        Returns:
            dict of the form {name: {remote_object_descriptor}}
        """
        return self._get_object_info("*")

    def _serialize(self, obj):
        """
        Serialize the given object using the serializer used for this HEROPeer. Currently only CBOR is supported.

        Args:
            obj: The object to serialized. Currently only built-in types and numpy arrays are supported.
        """
        return serdes.serialize(obj)

    def _deserialize(self, bytes: bytearray):
        """
        Deserialize the given byte string using the deserializer used for this HEROPeer. Currently only CBOR is
        supported.

        Args:
            bytes: bytearray to deserialize.
        """
        return serdes.deserialize(bytes)

    @local_only
    def _destroy_hero(self):
        # undeclare queryables
        for queryable in self._queryables:
            try:
                queryable.undeclare()
            except Exception:
                log.warning(f"could not undeclare queryable for {self._name}")

        # undeclare subscriptions
        for subscription in self._subscriptions:
            try:
                subscription.undeclare()
            except Exception:
                log.warning(f"could not undeclare subscription for {self._name}")

        # release zenoh session
        self._session_manager.release_session(self)

        self._hero_destroyed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._destroy_hero()

    def __del__(self):
        if hasattr(self, "_hero_destroyed") and not self._hero_destroyed:
            self._destroy_hero()


class HERO(HEROPeer):
    def __init__(self, name: str, realm: str = "heros", session_manager=None):
        self._name = name
        HEROPeer.__init__(self, realm=realm, session_manager=session_manager)

        self._endpoint_base_path = f"{self._ns_objects}/{self._realm}/{self._name}"
        self._endpoints = {
            "discover": f"{self._endpoint_base_path}/{self._ep_discover}",
            "capabilities": f"{self._endpoint_base_path}/{self._ep_capabilities}",
            "health": f"{self._endpoint_base_path}/{self._ep_health}",
        }

    def _query_endpoint(self, endpoint: str, *args, **kwargs) -> list:
        """
        Send a query to an endpoint.
        This is a wrapper for _query_selector that enforces to talk to the endpoint of the remote object.

        Args:
            endpoint: endpoint within this HERO. If the given endpoint does not start with the endpoint base path,
                the endpoint base path is prepended to generate a zenoh selector.
        """
        if not endpoint.startswith(self._endpoint_base_path):
            endpoint = "/".join([self._endpoint_base_path, endpoint])
        try:
            return self._query_selector(endpoint, *args, **kwargs)[0]
        except IndexError:
            return None

    def _subscribe_endpoint(self, endpoint: str, callback: callable, *args, **kwargs):
        """
        Subscribe to an endpoint of this HERO.
        This is a wrapper for _subscribe_selector that enforces to talk to the endpoint of the remote object.

        Args:
            endpoint: endpoint within this HERO. If the given endpoint does not start with the endpoint base path,
                the endpoint base path is prepended to generate a zenoh selector.
            callback:  method to be called for messages that match the selector. The method needs to accept one
                argument which is the deserialized payload of the message.
        """
        if not endpoint.startswith(self._endpoint_base_path):
            endpoint = "/".join([self._endpoint_base_path, endpoint])

        self._subscribe_selector(endpoint, lambda _, data: callback(data), *args, **kwargs)


class RemoteHERO(HERO):
    """
    Creates a local stub object from a remote HERO such that it seems like the remote object is a local object.
    The remote HERO is identified by its name and has to be available at the given realm.

    Attribute and method capabilities of the remote object are directly mapped to attributes and methods of the
    stub object, respectively. The signature of the methods is adapted accordingly. The remote attributes do not
    exist locally but are directly changed and read on the remote end. Event capabilities of the remote object
    are mapped to `RemoteEvent` objects that are members of this class. By connecting one or more callbacks to this
    event, the RemoteHERO can react on events triggered at the remote site.

    To be able to attach attributes to this class, every instance of a `RemoteHERO` is created from a dynamically
    generated child class of `RemoteHERO` with the name `RemoteHERO_<realm>_<HERO name>`.

    Note:
        To discover which objects are available in a certain realm, see :class:HEROObserver.

    Args:
        name: name/identifier of the remote object
        realm: realm (think namespace) at which the object is registered. default is "heros"
    """

    def __new__(cls, name: str, realm: str = "heros", *args, **kwargs):
        # We make individual classes for each object such that we can use setter and getter independently
        # for each object
        return super().__new__(type(f"RemoteHERO_{realm}_{name}", (cls,), {}))

    def __init__(self, name: str, realm: str = "heros", *args, **kwargs):
        HERO.__init__(self, name, realm, *args, **kwargs)

        object_info = self._discover()

        if self._name not in object_info:
            raise NameError(
                f"Remote Object with name {self._name} not found. Available objects are{list(object_info.keys())}"
            )

        self._hero_tags = object_info[self._name].get("tags", set())
        self._hero_implements = object_info[self._name].get("implements", set())

        self._remote_capabilities = self._get_capabilities()
        self._setattr_remote_capabilities()

        self._liveliness_subscription = self._session.liveliness().declare_subscriber(
            self._endpoints["health"], self._liveliness_changed
        )

    def _liveliness_changed(self, sample):
        log.debug(f"liveliness of remote object changed -> {sample}")

    def _get_capabilities(self):
        """
        Obtain capabilities from remote object.

        Returns:
            list[Capability]: List of capabilities of the remote device
        """
        return [Capability.from_dict(cap_dict) for cap_dict in self._query_endpoint(self._endpoints["capabilities"])]

    def _setattr_remote_capabilities(self):
        """
        Attach functions to the instance that reflect the name and signature of the capabilities of
        the remote object.
        """
        for cap in self._remote_capabilities:
            # create stub function
            if isinstance(cap, MethodCapability):

                def f(*args, _cap=cap, **kwargs):
                    return self._query_endpoint(_cap.name, payload=_cap.call_dict(*args, **kwargs))

                # attach stub function to self
                setattr(self, cap.name, mark_hero_method(f))
                getattr(self, cap.name).__signature__ = cap.to_signature()
                getattr(self, cap.name).__name__ = cap.name
                getattr(self, cap.name).__self__ = self

            elif isinstance(cap, AttributeCapability):

                def f_getter(_cap, self):
                    return self._query_endpoint(_cap.name)

                def f_setter(_cap, self, value):
                    # TODO Type checking
                    return self._query_endpoint(_cap.name, payload=value)

                # attach property to class
                setattr(self.__class__, cap.name, property(partial(f_getter, cap), partial(f_setter, cap)))

            elif isinstance(cap, EventCapability):
                remote_event = RemoteEventDescriptor()
                setattr(self.__class__, cap.name, remote_event)
                getattr(self, cap.name).__name__ = cap.name
                self._subscribe_endpoint(cap.name, getattr(self, cap.name))  # calls __call__

    def __eq__(self, other):
        return (
            self.__class__.__name__ == other.__class__.__name__
            and self._realm == other._realm
            and self._name == other._name
        )

    @local_only
    def _destroy_hero(self):
        self._liveliness_subscription.undeclare()
        super()._destroy_hero()

    def __hash__(self):
        return hash((self.__class__.__name__, self._realm, self._name))


class LocalHERO(HERO):
    """
    Base class for objects exposed through HEROS.
    Any object that should be able to be accessed remotely must be based off this class.

    Args:
        name: name/identifier under which the object is available. Make sure this name is unique in the realm.
        realm: realm the HERO should exist in. default is "heros"
        implements: list of interfaces that are implemented by the hero
        tags: list of tags to identify and classify the hero
    """

    def __init__(
        self,
        name: str,
        *args,
        realm: str = "heros",
        implements: list[str] | None = None,
        tags: list[str] | None = None,
        **kwargs,
    ):
        implements = [] if implements is None else implements
        tags = [] if tags is None else tags

        HERO.__init__(self, name, realm, **kwargs)

        self._capabilities()

        log.debug(f"init object with name {name} and capabilities {self.capabilities}")

        def discover_callback(query):
            ro_descriptor = {
                "name": self._name,
                "class": self.__class__.__name__,
                "implements": set(implements + getattr(self, "_hero_implements", [])),
                "tags": set(tags + getattr(self, "_hero_tags", [])),
            }
            query.reply(self._endpoints["discover"], self._serialize(ro_descriptor), encoding=self._default_encoding)

        def capabilities_callback(query):
            query.reply(
                self._endpoints["capabilities"],
                self._serialize([cap.to_dict() for cap in self.capabilities]),
                encoding=self._default_encoding,
            )

        self._declare_queryable(self._endpoints["discover"], discover_callback)
        self._declare_queryable(self._endpoints["capabilities"], capabilities_callback)

        # create liveliness token such that our presence can be monitored
        self.liveliness_token = self._session.liveliness().declare_token(self._endpoints["health"])

    def _capabilities(self):
        """
        Analyze ourself (i.e. the current object) and automatically generate the capabilities of the HERO from this.
        For every method that doesn't start with _ a method capability is announced. Every defined class attribute
        becomes an attribute capability. Every method that is defined in the class with the @event decorator becomes
        an event.

        While scanning for the capabilities, this method directly creates the necessary callbacks and defines the zenoh
        queryables for the capabilities.
        """
        self.capabilities = []
        for member_name in dir(self.__class__):
            # skip members we do not want to expose
            exclude = any(
                [
                    member_name.startswith("_"),
                    member_name in dir(LocalHERO),
                    is_local_only(getattr(self.__class__, member_name)),
                ]
            )
            if exclude and (not is_force_remote(getattr(self.__class__, member_name))):
                continue

            if callable(getattr(self, member_name)):
                if is_hero_event(getattr(self, member_name)):
                    log.debug(f"found event with name {member_name}!")
                    cap = EventCapability(name=member_name)
                    wrapper = None
                else:
                    try:
                        cap = MethodCapability.from_method(name=member_name, m=getattr(self, member_name))
                    except ValueError:
                        # this occurs if the callable cannot be inspected, we thus skip it
                        log.warn(f"Skipping {getattr(self, member_name)} since the signature cannot be inferred!")
                        continue

                    # create queryable for the capability
                    def wrapper(_cap, query):
                        params = self._deserialize(query.payload.to_bytes())
                        log.debug(f"I should call {_cap.name} with parameters {params}")

                        try:
                            # the actual method call
                            return_value = getattr(self, _cap.name)(**params)

                            # send back the result
                            query.reply(
                                f"{self._endpoint_base_path}/{_cap.name}",
                                self._serialize(return_value),
                                encoding=self._default_encoding,
                            )
                        except Exception as e:
                            query.reply_err(
                                self._serialize(str(e) + "\n\n" + "".join(traceback.format_tb(e.__traceback__))),
                                encoding=self._default_encoding,
                            )

                    log.debug(f"register method queryable for {self._endpoint_base_path}/{member_name}")

            else:
                cap = AttributeCapability(name=member_name, type=type(getattr(self, member_name)).__name__)

                def wrapper(_cap, query):
                    if query.payload:
                        setattr(self, _cap.name, self._deserialize(query.payload.to_bytes()))
                        log.debug(f"I should update {_cap.name}")
                    else:
                        log.debug(f"I should return value of {_cap.name}")

                        # send back the result
                        query.reply(
                            f"{self._endpoint_base_path}/{_cap.name}",
                            self._serialize(getattr(self, _cap.name)),
                            encoding=self._default_encoding,
                        )

            if wrapper is not None:
                self._declare_queryable(f"{self._endpoint_base_path}/{member_name}", partial(wrapper, cap))
            self.capabilities.append(cap)

    @local_only
    def _destroy_hero(self):
        try:
            self.liveliness_token.undeclare()
        except Exception:
            log.warn(f"could not undeclare liveliness token for {self._name}")
        super()._destroy_hero()

    @force_remote
    def _connect_local_hero_callback(self, event: callable, remote_hero_method: callable, origin: str = None) -> str:
        """
        Connect a method of `RemoteHERO` as a callback to an event of the `LocalHERO`.
        This leads to a new, direct P2P connection between the `RemoteHERO` and the `LocalHERO` to call the method.

        Args:
            event: the event `callable`, i.e. a method that is decorated with `@event` in the `LocalHERO`.
            remote_hero_method: `callable` to connect as a callback.
            origin: optional `str` indicating the semantic origin of the connection.

        Returns:
            str: name of the callback.
        """
        return getattr(self, event.__name__).connect(remote_hero_method, origin)

    @force_remote
    def _disconnect_local_hero_callback(self, event: callable, remote_hero_method: callable) -> bool:
        """
        Disconnect a method of `RemoteHERO` from an event of the `LocalHERO`.

        Args:
            event: the event `callable`, i.e. a method that is decorated with `@event` in the `LocalHERO`.
            remote_hero_method: `callable` to connect as a callback.

        Returns:
            bool: truth value if the remote method was indeed a callback.
        """
        return getattr(self, event.__name__).disconnect(remote_hero_method)

    @force_remote
    def _get_local_hero_callbacks(self, event: callable) -> list:
        """
        Get a list of dictionary representations of the callbacks of an event of the `LocalHERO`.

        Args:
            event: the event `callable`, i.e. a method that is decorated with `@event` in the `LocalHERO`.

        Returns:
            list: dictionary representations of the callbacks.
        """
        return getattr(self, event.__name__).get_callbacks()


class EventObserver(HEROPeer):
    """
    A class that can observe and handle the data emitted by one or more HEROs from a defined event name.
    In particular, this class provides an efficient way to listen to the data emitted by multiple HEROs in
    the realm. By not instantiating the HEROs themselves but just subscribing to the topics for the event, this
    reduces the pressure on the backing zenoh network. If, however, only the data of a few HEROs should be observed,
    it might make more sense to just instantiate the according RemoteHEROs and connect a callback to their events.

    Args:
        object_selector: Selector to specify which objects to observe. This becomes part of a zenoh selector and thus
        can be anything that makes sense in the selector. Use :code:`*` to observe all HEROs in the realm.
        event_name: Name of the event to observe.
    """

    def __init__(self, object_selector: str, event_name: str, *args, **kwargs):
        HEROPeer.__init__(self, *args, **kwargs)
        self._object_selector = object_selector
        self._event_name = event_name

        self._event_callbacks = {}

        zenoh_selector = "/".join([self._ns_objects, self._realm, object_selector, self._event_name])
        self._subscription = self._subscribe_selector(zenoh_selector, self._handle_event)

    def _handle_event(self, key_expr: str, data):
        # make a copy in case a callback is removed during iteration
        _event_callbacks = self._event_callbacks.copy()
        for uid, cb in _event_callbacks.items():
            try:
                object_name = object_name_from_keyexpr(str(key_expr), self._ns_objects, self._realm, self._event_name)
                cb(object_name, data)
            except Exception as e:
                log.error(f"Could not call callback {uid}:{cb} for event: {e}")

    def register_callback(self, func: callable) -> str | bool:
        """
        Register a callback that should be called on events.

        Args:
            func: Function to call.

        Returns:
            The uuid of the callback or False if the callback was already present.
        """
        if func not in self._event_callbacks.values():
            uid = str(uuid.uuid4())
            self._event_callbacks[uid] = func
            return uid
        return False

    def remove_callback(self, func: callable) -> bool:
        """
        Remove a callback.

        Args:
            func: Function to remove.

        Returns:
            True if the callback could be removed, False otherwise.
        """
        for uid, cb in self._event_callbacks.items():
            if cb == func:
                return self.remove_callback_uid(uid)
        return False

    def remove_callback_uid(self, uid: str) -> bool:
        """
        Remove a callback by its uid.

        Args:
            uid: Uid of the callback.

        Returns:
            True
        """
        del self._event_callbacks[uid]
        return True


class HEROObserver(HEROPeer):
    """
    A HEROObserver keeps track of the HEROs in a given realm by monitoring its zenoh liveliness tokens.
    The member attribute ``known_objects`` always holds a list of all HEROs known to the observer.

    Args:
        realm: Name of the realm that this HEROPeer belongs to. (default: heros)
        session: optional zenoh session to use. If none is provided, a new zenoh session will be started
    """

    def __init__(self, *args, **kwargs):
        HEROPeer.__init__(self, *args, **kwargs)

        self.known_objects = self._discover()
        self._object_added_callbacks = []
        self._object_removed_callbacks = []

        self._session.liveliness().declare_subscriber(
            f"{self._ns_objects}/{self._realm}/*/{self._ep_health}", self._handle_status_change
        )

    def _handle_status_change(self, sample):
        """
        Handle the status change of liveliness tokens.
        """
        object_name = object_name_from_keyexpr(str(sample.key_expr), self._ns_objects, self._realm, self._ep_health)

        log.debug(f"status change from {sample.key_expr} -> {sample.kind}")

        if sample.kind == zenoh.SampleKind.PUT:
            self.known_objects.update(self._get_object_info(object_name))
            for f in self._object_added_callbacks:
                f(object_name)
        elif sample.kind == zenoh.SampleKind.DELETE and len(self._get_object_info(object_name)) == 0:
            if object_name in self.known_objects:
                del self.known_objects[object_name]
            for f in self._object_removed_callbacks:
                f(object_name)

    def register_object_added_callback(self, func: callable) -> None:
        """
        Register a callback that should be called when a new HERO joins the realm.

        Args:
            func: function to call when a new HERO joins the realm
        """
        if func not in self._object_added_callbacks:
            self._object_added_callbacks.append(func)

    def register_object_removed_callback(self, func: callable) -> None:
        """
        Register a callback that should be called when a new HERO leaves the realm.

        Args:
            func: function to call when a new HERO leaves the realm
        """
        if func not in self._object_removed_callbacks:
            self._object_removed_callbacks.append(func)

    def get_object(self, object_name: str) -> RemoteHERO:
        """
        Get the RemoteHERO object for the HERO with the given name.

        Args:
            object_name: name of the HERO
        """
        if object_name in self.known_objects.keys():
            return RemoteHERO(object_name, self._realm, session_manager=self._session_manager)
        else:
            raise AttributeError(f"Object with name {object_name} not known")
