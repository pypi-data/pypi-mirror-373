from talkgooder.talkgooder import isAre


def test_isare_int_is():
    assert isAre(1) == "is"


def test_isare_int_are():
    assert isAre(0) == "are"


def test_isare_float_is():
    assert isAre(1.0) == "are"


def test_isare_float_are():
    assert isAre(2.1) == "are"
