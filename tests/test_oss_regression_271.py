import pytest

from configobj import ConfigObj


@pytest.mark.parametrize("delimiter", ['"""', "'''"])
@pytest.mark.parametrize("list_values", [True, False])
def test_triple_quotes_and_hash_round_trip(tmp_path, delimiter, list_values):
    filename = tmp_path / "config.ini"
    config = ConfigObj(str(filename), encoding="utf-8", list_values=list_values)
    prefix = "'" if delimiter == '"""' else '"'
    value = prefix + delimiter + "hello" + delimiter + " # world"
    config["foo"] = {"bar": value}

    config.write()
    config.reload()

    assert config["foo"]["bar"] == value
