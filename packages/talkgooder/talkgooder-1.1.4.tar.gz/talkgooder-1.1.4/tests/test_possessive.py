from talkgooder.talkgooder import possessive


def test_no_trailing_s_lower():
    assert possessive("cat") == "cat's"


def test_no_trailing_s_upper():
    assert possessive("CAT") == "CAT'S"


def test_no_trailing_s_lower_force_upper():
    assert possessive("cat", caps_mode=1) == "cat'S"


def test_no_trailing_s_upper_force_lower():
    assert possessive("CAT", caps_mode=2) == "CAT's"


def test_trailing_s():
    assert possessive("cats") == "cats'"
