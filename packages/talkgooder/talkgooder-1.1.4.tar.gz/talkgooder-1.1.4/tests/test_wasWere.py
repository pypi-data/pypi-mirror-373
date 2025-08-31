from talkgooder.talkgooder import wasWere


def test_waswere_int_is():
    assert wasWere(1) == "was"


def test_waswere_int_are():
    assert wasWere(0) == "were"


def test_waswere_float_is():
    assert wasWere(1.0) == "were"


def test_waswere_float_are():
    assert wasWere(2.1) == "were"
