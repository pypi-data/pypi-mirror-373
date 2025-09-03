import zenoh
import json
import atexit


class ZenohSessionManager:
    def __init__(self, config_dict: dict | None = None):
        config_dict = {} if config_dict is None else config_dict
        self._config_dict = config_dict
        self._session = None
        self._referrers = []

    def request_session(self, obj: object) -> zenoh.Session:
        """
        Request the global zenoh session.

        Args:
            obj: The object that requests the session
        """
        if self._session is None:
            config = zenoh.Config()
            for key, value in self._config_dict.items():
                config.insert_json5(key, json.dumps(value))
            self._session = zenoh.open(config)
            atexit.register(self._session.close)

        if obj not in self._referrers:
            self._referrers.append(obj)

        return self._session

    def release_session(self, obj: object) -> None:
        """
        Release from the global zenoh session.

        Args:
            obj: The object that wants to release from the global zenoh session
        """
        if obj in self._referrers:
            del self._referrers[self._referrers.index(obj)]
        else:
            return
        if len(self._referrers) <= 0 and self._session is not None:
            self._session.close()
            self._session = None

    def update_config(self, config_dict: dict) -> None:
        self._config_dict.update(config_dict)

    def force_close(self) -> None:
        if self._session is not None:
            self._session.close()
        self._referrers = []


session_manager = ZenohSessionManager()
