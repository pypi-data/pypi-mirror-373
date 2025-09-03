HERO_EVENT_ATTRIBUTE = "hero_event"
HERO_METHOD_ATTRIBUTE = "hero_method"
LOCAL_ONLY_ATTRIBUTE = "local_only"
FORCE_REMOTE_ATTRIBUTE = "force_remote"


def _mark(func: callable, marker: str) -> callable:
    """
    Mark a callable with a provided marker.

    Args:
        func: callable to mark
        marker: attribute name at which to mark the callable

    Returns:
        The marked callable.
    """
    setattr(func, marker, True)
    return func


def _is_marked(func: callable, marker: str) -> bool:
    """
    Inspect if a callable is marked with a provided marker.

    Args:
        func: callable to check
        marker: attribute name of the attribute to check

    Returns:
        The value of the marker.
        `False` if the marker is not present.
    """
    return getattr(func, marker, False)


# I know these could be perfectly auto-generated
# Yet, we do it explicitly here for the sake of debugging
def mark_hero_event(func: callable) -> callable:
    """
    Mark a callable as a event.

    Args:
        func: callable to mark

    Returns:
        The marked callable.
    """
    return _mark(func, HERO_EVENT_ATTRIBUTE)


def mark_hero_method(func: callable) -> callable:
    """
    Mark a callable as a method of a (remote) hero.

    Args:
        func: callable to mark

    Returns:
        The marked callable.
    """
    return _mark(func, HERO_METHOD_ATTRIBUTE)


def mark_local_only(func: callable) -> callable:
    """
    Mark a callable is local only.

    Args:
        func: callable to mark

    Returns:
        The marked callable.
    """
    return _mark(func, LOCAL_ONLY_ATTRIBUTE)


# rename mark_local_only to use as a decorator
local_only = mark_local_only


def mark_force_remote(func: callable) -> callable:
    """
    Mark a callable as force remote.

    Args:
        func: callable to mark

    Returns:
        The marked callable.
    """
    return _mark(func, FORCE_REMOTE_ATTRIBUTE)


# rename mark_force_remote to use as a decorator
force_remote = mark_force_remote


def is_hero_event(func: callable) -> bool:
    """
    Check if a callable is a event.

    Args:
        func: callable to check

    Returns:
        The value of the marker.
        `False` if the marker is not present.
    """
    return _is_marked(func, HERO_EVENT_ATTRIBUTE)


def is_hero_method(func: callable) -> bool:
    """
    Check if a callable is a method of a (remote) hero.

    Args:
        func: callable to check

    Returns:
        The value of the marker.
        `False` if the marker is not present.
    """
    return _is_marked(func, HERO_METHOD_ATTRIBUTE)


def is_local_only(func: callable) -> bool:
    """
    Check if a callable is a local only.

    Args:
        func: callable to check

    Returns:
        The value of the marker.
        `False` if the marker is not present.
    """
    return _is_marked(func, LOCAL_ONLY_ATTRIBUTE)


def is_force_remote(func: callable) -> bool:
    """
    Check if a callable is a force remote.

    Args:
        func: callable to check

    Returns:
        The value of the marker.
        `False` if the marker is not present.
    """
    return _is_marked(func, FORCE_REMOTE_ATTRIBUTE)
