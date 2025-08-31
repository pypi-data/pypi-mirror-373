from talkgooder.talkgooder import num2word


def test_integer_in_range():
    assert num2word(5) == "five"


def test_integer_below_range():
    assert num2word(0) == "0"


def test_integer_above_range():
    assert num2word(10) == "10"
