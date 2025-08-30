#  Copyright (c) 2024. Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated
#  documentation files (the “Software”), to deal in the Software without restriction, including
#  without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
#  Software, and to permit
#  persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or
#  substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#  BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
#  EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
#  CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
from datetime import date

import pytest

from YMLEditor.yaml_config import YamlConfig

# Define constants for YAML file content
VALID_YAML_FILE = "config.yaml"


@pytest.fixture
def valid_yaml_data():
    return """
---
CRS1: -t_srs epsg:3857
LAYER: B
FILES:
  A: null
  B: WESTMAN.tif
  C: "*_topo.tif"
languages:
  - YAML
  - JAVA
  - XML
name: yaml
rank: 1
born: 2001
published: true
approved: true
date: 1987-05-24
time: 10:00
hash_example: "This string contains # as text"
file_name: -file.txt
"[part1, part2]": This is a complex key with a sequence
quote: ‘YAML is the “best” configuration language’
doublequote: “ Yes, the ‘best’ “
colors:
  - red
  - green
  - blue
person:
  name: Alice
  age: 30
  location: Wonderland
items:
  - id: 1
    name: Item A
  - id: 2
    name: Item B
key_with_empty_value: null
key_with_null_value: null
another_null_value: null
message1: |
  even though it looks like this is a multiline message, it is actually not
message2: |
  this is
  a real multiline
  message
message3: >+
  This block line Will be interpreted as a single line with a newline
  character at the end
vars:
  service1:
    config:
      env: prod
      retries: 3
      version: 4.8
  service2:
    config:
      env: prod
      retries: 3
      version: 4.8
  service3:
    config:
      env: prod
      retries: 3
      version: 4.8
vars2:
  service1:
    config:
      env: prod
      retries: 3
      version: 4.8
  service2:
    config:
      env: prod
      retries: 3
      version: 5
  service3:
    config:
      env: prod
      retries: 3
      version: 4.2
"""


@pytest.fixture
def invalid_yaml_data():
    return """
CRS1: -t_srs epsg:3857
unbalanced brackets: ][
    """


@pytest.fixture
def config():
    return YamlConfig()


@pytest.fixture
def loaded_config(config, valid_yaml_data, tmpdir):
    """Fixture to load configuration from valid YAML data."""
    file_path = tmpdir.join(VALID_YAML_FILE)
    file_path.write(valid_yaml_data)
    config.load(file_path)
    return config


# TEST READ VALUES
def test_read_key(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["CRS1"] == "-t_srs epsg:3857"
    assert loaded_config["LAYER"] == 'B'
    assert loaded_config["FILES"] == {'A': None, 'B': 'WESTMAN.tif', 'C': '*_topo.tif'}


def test_flow_style_sequences(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["colors"] == ["red", "green", "blue"]
    assert loaded_config["languages"] == ["YAML", "JAVA", "XML"]


def test_flow_style_maps(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["person"] == {"name": "Alice", "age": 30, "location": "Wonderland"}


def test_empty_and_null_values(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["key_with_empty_value"] is None
    assert loaded_config["key_with_null_value"] is None
    assert loaded_config["another_null_value"] is None


def test_special_characters(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["quote"] == "‘YAML is the “best” configuration language’"
    assert loaded_config["doublequote"] == "“ Yes, the ‘best’ “"
    assert loaded_config["time"] == 600
    assert loaded_config["date"] == date(1987, 5, 24)
    assert loaded_config["file_name"] == "-file.txt"
    assert loaded_config["hash_example"] == "This string contains # as text"


def test_special_characters2(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["hash_example"] == "This string contains # as text"


def test_multiline_literals1(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["message1"] == ("even though it looks like this is a multiline message, "
                                         "it is actually not\n")


def test_multiline_literals2(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["message2"] == "this is\na real multiline\nmessage\n"


def test_aliases_and_references(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config["vars"]["service1"]["config"]["env"] == "prod"
    assert loaded_config["vars"]["service2"]["config"][
               "env"] == "prod"  # should reference service1 config
    assert loaded_config["vars"]["service3"]["config"][
               "retries"] == 3  # should reference service1 config


def test_read_dot_key(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config.get("FILES.B") == 'WESTMAN.tif'


def test_read_indirect(loaded_config, valid_yaml_data, tmpdir):
    assert loaded_config.get("FILES.@LAYER") == 'WESTMAN.tif'


def test_data_types(loaded_config, valid_yaml_data, tmpdir):
    # Test correct data types and values
    assert isinstance(loaded_config["name"], str)
    assert loaded_config["name"] == "yaml"

    assert isinstance(loaded_config["rank"], int)
    assert loaded_config["rank"] == 1

    assert isinstance(loaded_config["born"], int)
    assert loaded_config["born"] == 2001

    assert isinstance(loaded_config["published"], bool)
    assert loaded_config["published"] is True

    assert isinstance(loaded_config["approved"], bool)
    assert loaded_config["approved"] is True


# TEST SET VALUES
def test_set_and_get_setting(loaded_config, valid_yaml_data, tmpdir):
    loaded_config["NEW_KEY"] = "new_value"
    assert loaded_config["NEW_KEY"] == "new_value"


def test_set_and_get_multi(loaded_config, valid_yaml_data, tmpdir):
    loaded_config["NEW_KEY.A"] = "new_value"
    assert loaded_config["NEW_KEY.A"] == "new_value"


def test_set_and_get_indirect(loaded_config, valid_yaml_data, tmpdir):
    loaded_config.set("FILES.@LAYER", "value2")
    assert loaded_config.get("FILES.@LAYER") == "value2"
    assert loaded_config.get("FILES.B") == "value2"

