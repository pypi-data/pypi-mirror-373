def test_local_callback_on_LocalHERO(local_hero_device, local_method):
    local_hero_device.my_event.connect(local_method)
    local_hero_device.my_event("hello")
    local_method.assert_called_once_with("hello")


def test_local_callback_on_RemoteHERO(remote_hero_device, local_method):
    remote_hero_device.my_event.connect(local_method)
    remote_hero_device.my_event("hello")
    local_method.assert_called_once_with("hello")
