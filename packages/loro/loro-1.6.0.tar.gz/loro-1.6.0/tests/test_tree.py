from loro import LoroDoc, LoroText,  ValueOrContainer


def test_tree():
    doc = LoroDoc()
    tree = doc.get_tree("tree")
    root = tree.create()
    child = tree.create(root)
    assert tree.children(root) == [child]
    assert tree.children(None) == [root]

    child_meta = tree.get_meta(child)
    text = LoroText()
    text.insert(0, "hi")
    child_meta.insert_container("a", text)
    child_meta.insert("b", value="basic")

    container = child_meta.get(key="a")
    assert ValueOrContainer.is_container(container)
    assert isinstance(container.container, LoroText)
    assert container.container.to_string() == "hi"

    value = child_meta.get(key="b")
    assert ValueOrContainer.is_value(value)
    assert value.value == "basic"
