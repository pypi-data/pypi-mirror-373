from loro import LoroDoc


def test_counter_int():
    doc = LoroDoc()
    counter = doc.get_counter("counter")
    counter.increment(1)
    doc.commit()
    assert counter.value == 1
    counter.decrement(1)
    doc.commit()
    assert counter.value == 0


def test_counter_float():
    doc = LoroDoc()
    counter = doc.get_counter("counter")
    counter.increment(1.2)
    doc.commit()
    assert counter.value == 1.2
    counter.decrement(2)
    doc.commit()
    assert counter.value == -0.8
