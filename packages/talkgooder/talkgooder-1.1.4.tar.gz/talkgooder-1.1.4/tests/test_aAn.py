from talkgooder.talkgooder import aAn


def test_vowel_lower():
    assert aAn("apple") == "an"


def test_vowel_upper():
    assert aAn("Apple") == "an"


def test_consonont_lower():
    assert aAn("cat") == "a"


def test_consonont_upper():
    assert aAn("Cat") == "a"


def test_int_a():
    assert aAn(1) == "a"


def test_float_a():
    assert aAn(1.1) == "a"


def test_int_an():
    assert aAn(800) == "an"


def test_float_an():
    assert aAn(800.1) == "an"


def test_int_an_18():
    assert aAn(18) == "an"


def test_float_an_18():
    assert aAn(18.1) == "an"
