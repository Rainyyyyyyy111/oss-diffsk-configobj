import math

import pytest

from configobj import ConfigObj, UnreprError, unrepr


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite_float_round_trip(tmp_path, value):
    filename = str(tmp_path / 'nonfinite.ini')
    original = ConfigObj(filename, unrepr=True)
    original['value'] = value
    original.write()

    restored = None
    error = None
    try:
        restored = ConfigObj(filename, unrepr=True)
    except UnreprError as caught:
        error = caught

    assert error is None, 'Values written in unrepr mode must be readable'
    if math.isnan(value):
        assert math.isnan(restored['value'])
    else:
        assert restored['value'] == value


def test_nested_nonfinite_float_round_trip():
    original = ConfigObj(unrepr=True)
    original['value'] = [float('nan'), {'nan': float('inf')}, (-float('inf'),)]

    restored = None
    error = None
    try:
        restored = ConfigObj(original.write(), unrepr=True)
    except UnreprError as caught:
        error = caught

    assert error is None, 'Nested non-finite floats must be readable'
    assert math.isnan(restored['value'][0])
    assert restored['value'][1] == {'nan': float('inf')}
    assert restored['value'][2] == (-float('inf'),)


@pytest.mark.parametrize('text', ["'nan'", "'inf'", "{'nan': 'inf'}", "['nan', 'inf']"])
def test_nonfinite_words_in_strings_are_preserved(text):
    original = ConfigObj(['value = ' + text], unrepr=True)

    assert ConfigObj(original.write(), unrepr=True) == original


@pytest.mark.parametrize('text', ['missing', 'nan()', 'inf.real', 'nan + 1'])
def test_unrepr_still_rejects_nonliteral_expressions(text):
    with pytest.raises(ValueError):
        unrepr(text)


@pytest.mark.parametrize('text', ['nan', 'inf', '-inf'])
def test_normal_mode_keeps_float_names_as_strings(text):
    assert ConfigObj(['value = ' + text])['value'] == text


def test_nonfinite_name_with_leading_whitespace():
    value = None
    try:
        value = unrepr(' \tnan')
    except ValueError:
        pass

    assert value is not None, 'Leading whitespace must not prevent NaN parsing'
    assert math.isnan(value)
