from talkgooder.talkgooder import plural


# Singular words returned unmodified
def test_singular_irregular():
    assert plural("mouse", 1) == "mouse"


def test_singular_same():
    assert plural("shrimp", 1) == "shrimp"


def test_singular_special_s():
    assert plural("hello", 1) == "hello"


def test_singular_i():
    assert plural("cactus", 1) == "cactus"


def test_singular_a():
    assert plural("stratum", 1) == "stratum"


def test_singular_ices():
    assert plural("index", 1) == "index"


def test_singular_es():
    assert plural("match", 1) == "match"


def test_singular_y_no_ies():
    assert plural("toy", 1) == "toy"


def test_singular_ies():
    assert plural("jolly", 1) == "jolly"


def test_singular_ves():
    assert plural("hoof", 1) == "hoof"


def test_singular_s():
    assert plural("cat", 1) == "cat"


# Words that are the same singular and plural don't change
def test_zero_same():
    assert plural("shrimp", 0) == "shrimp"


def test_positive_integer_same():
    assert plural("shrimp", 2) == "shrimp"


def test_negative_integer_same():
    assert plural("shrimp", -2) == "shrimp"


def test_positive_float_same():
    assert plural("shrimp", 0.1) == "shrimp"


def test_negative_float_same():
    assert plural("shrimp", -0.1) == "shrimp"


def test_positive_float_1_same():
    assert plural("shrimp", 1.0) == "shrimp"


# Words that don't follow the rules
def test_zero_irregular():
    assert plural("mouse", 0) == "mice"


def test_positive_integer_irregular():
    assert plural("mouse", 2) == "mice"


def test_negative_integer_irregular():
    assert plural("mouse", -2) == "mice"


def test_positive_float_irregular():
    assert plural("mouse", 0.1) == "mice"


def test_negative_float_irregular():
    assert plural("mouse", -0.1) == "mice"


def test_positive_float_1_irregular():
    assert plural("mouse", 1.0) == "mice"


# Words that end in s for no reason other than Reasons
def test_zero_special_s():
    assert plural("hello", 0) == "hellos"


def test_positive_integer_special_s():
    assert plural("hello", 2) == "hellos"


def test_negative_integer_special_s():
    assert plural("hello", -2) == "hellos"


def test_positive_float_special_s():
    assert plural("hello", 0.1) == "hellos"


def test_negative_float_special_s():
    assert plural("hello", -0.1) == "hellos"


def test_positive_float_1_special_s():
    assert plural("hello", 1.0) == "hellos"


# Words that end in us and change to "i"
def test_zero_i():
    assert plural("cactus", 0) == "cacti"


def test_positive_integer_i():
    assert plural("cactus", 2) == "cacti"


def test_negative_integer_i():
    assert plural("cactus", -2) == "cacti"


def test_positive_float_i():
    assert plural("cactus", 0.1) == "cacti"


def test_negative_float_i():
    assert plural("cactus", -0.1) == "cacti"


def test_positive_float_1_i():
    assert plural("cactus", 1.0) == "cacti"


# Words that end in um and change to "a"
def test_zero_a():
    assert plural("stratum", 0) == "strata"


def test_positive_integer_a():
    assert plural("stratum", 2) == "strata"


def test_negative_integer_a():
    assert plural("stratum", -2) == "strata"


def test_positive_float_a():
    assert plural("stratum", 0.1) == "strata"


def test_negative_float_a():
    assert plural("stratum", -0.1) == "strata"


def test_positive_float_1_a():
    assert plural("stratum", 1.0) == "strata"


# Words that end in ix or ex and change to "ices"
def test_zero_ices():
    assert plural("index", 0) == "indices"


def test_positive_integer_ices():
    assert plural("index", 2) == "indices"


def test_negative_integer_ices():
    assert plural("index", -2) == "indices"


def test_positive_float_ices():
    assert plural("index", 0.1) == "indices"


def test_negative_float_ices():
    assert plural("index", -0.1) == "indices"


def test_positive_float_1_ices():
    assert plural("index", 1.0) == "indices"


# Words in the "es" match list
def test_zero_es():
    assert plural("match", 0) == "matches"


def test_positive_integer_es():
    assert plural("match", 2) == "matches"


def test_negative_integer_es():
    assert plural("match", -2) == "matches"


def test_positive_float_es():
    assert plural("match", 0.1) == "matches"


def test_negative_float_es():
    assert plural("match", -0.1) == "matches"


def test_positive_float_1_es():
    assert plural("match", 1.0) == "matches"


# Words that end in y but don't change to "ies"
def test_zero_y_no_ies():
    assert plural("toy", 0) == "toys"


def test_positive_integer_y_no_ies():
    assert plural("toy", 2) == "toys"


def test_negative_integer_y_no_ies():
    assert plural("toy", -2) == "toys"


def test_positive_float_y_no_ies():
    assert plural("toy", 0.1) == "toys"


def test_negative_float_y_no_ies():
    assert plural("toy", -0.1) == "toys"


def test_positive_float_1_y_no_ies():
    assert plural("toy", 1.0) == "toys"


# Words that end in y and change to "ies"
def test_zero_ies():
    assert plural("jolly", 0) == "jollies"


def test_positive_integer_ies():
    assert plural("jolly", 2) == "jollies"


def test_negative_integer_ies():
    assert plural("jolly", -2) == "jollies"


def test_positive_float_ies():
    assert plural("jolly", 0.1) == "jollies"


def test_negative_float_ies():
    assert plural("jolly", -0.1) == "jollies"


def test_positive_float_1_ies():
    assert plural("jolly", 1.0) == "jollies"


# Words that are not in "es" or "ies" match list
def test_zero_integer_ves():
    assert plural("hoof", 0) == "hooves"


def test_positive_integer_ves():
    assert plural("hoof", 2) == "hooves"


def test_negative_singular_ves():
    assert plural("hoof", -1) == "hooves"


def test_negative_integer_ves():
    assert plural("hoof", -2) == "hooves"


def test_positive_float_ves():
    assert plural("hoof", 0.1) == "hooves"


def test_positive_float_1_ves():
    assert plural("hoof", 1.0) == "hooves"


def test_negative_float_ves():
    assert plural("hoof", -0.1) == "hooves"


# Words that are not in "es" or "ies" match list
def test_zero_integer_s():
    assert plural("cat", 0) == "cats"


def test_positive_integer_s():
    assert plural("cat", 2) == "cats"


def test_negative_singular_s():
    assert plural("cat", -1) == "cats"


def test_negative_integer_s():
    assert plural("cat", -2) == "cats"


def test_positive_float_s():
    assert plural("cat", 0.1) == "cats"


def test_positive_float_1_s():
    assert plural("cat", 1.0) == "cats"


def test_negative_float_s():
    assert plural("cat", -0.1) == "cats"


# Capitalized variants
def test_zero_es_all_upper():
    assert plural("MATCH", 0) == "MATCHES"


def test_zero_es_part_upper():
    assert plural("MaTcH", 0) == "MaTcHes"


def test_zero_ies_all_upper():
    assert plural("JOLLY", 0) == "JOLLIES"


def test_zero_ies_part_upper():
    assert plural("JoLly", 0) == "JoLlies"


def test_zero_s_all_upper():
    assert plural("CAT", 0) == "CATS"


def test_zero_s_part_upper():
    assert plural("CaT", 0) == "CaTs"


def test_force_upper():
    assert plural("CaT", 0, caps_mode=1) == "CaTS"


def test_force_lower():
    assert plural("CAT", 0, caps_mode=2) == "CATs"


# Additional special cases
def test_additional_same():
    assert plural("cat", 2, addl_same=["cat", "dog"]) == "cat"


def test_additional_special_s():
    assert plural("jolly", 2, addl_special_s=["jolly", "giggle"]) == "jollys"


def test_additional_irregular():
    assert plural("jolly", 2, addl_irregular={"jolly": "giggles"}) == "giggles"
