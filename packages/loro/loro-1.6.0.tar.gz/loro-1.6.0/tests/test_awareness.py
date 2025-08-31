from loro import Awareness

def test_awareness():
    awareness = Awareness(1, 1000)
    awareness.local_state = {"a": 1}
    assert awareness.local_state == {"a": 1}
