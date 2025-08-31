from bluer_objects.graphics import screen


def test_graphics_screen_get_size():

    size = screen.get_size()

    assert len(size) == 2
