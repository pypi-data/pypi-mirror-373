from fediverse_pasture_inputs import available

from .navigation import group_names, order_available_by_group


def test_group_names():
    defined = {in_data.group for in_data in available.values()}

    assert defined == set(group_names)


def test_order_available_by_group():
    result = order_available_by_group()

    for x in group_names:
        assert len(result[x]) > 0
