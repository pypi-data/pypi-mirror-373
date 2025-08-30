import pytest

from dpgcontainers.containers import Group
from dpgcontainers.exceptions import NamedChildNotFound


def test_named_children():
    inner_1 = Group()
    inner_2 = Group()
    outer = Group()(named_1=inner_1, named_2=inner_2)

    found = outer.search_named_children('named_2')
    assert found is inner_2

    outer.remove_child(inner_1)

    found = outer.search_named_children('named_2')
    assert found is inner_2

    inner_3 = Group()
    outer.add_child(inner_3, name='named_3')
    outer.remove_child(inner_2)
    found = outer.search_named_children('named_3')
    assert found is inner_3

    with pytest.raises(NamedChildNotFound):
        outer.search_named_children('named_2')
