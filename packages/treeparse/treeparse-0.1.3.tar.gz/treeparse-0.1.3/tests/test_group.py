from treeparse import group


def test_group_model():
    grp = group(name="test", subgroups=[], commands=[])
    assert grp.name == "test"
