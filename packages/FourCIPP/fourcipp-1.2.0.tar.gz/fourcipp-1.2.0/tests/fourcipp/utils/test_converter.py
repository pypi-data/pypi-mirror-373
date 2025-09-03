# The MIT License (MIT)
#
# Copyright (c) 2025 FourCIPP Authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Test Converter class."""

import numpy as np
import pytest

from fourcipp.utils.converter import Converter
from fourcipp.utils.dict_utils import compare_nested_dicts_or_lists


# create a fixture for the converter
@pytest.fixture
def converter():
    """Fixture for the Converter class."""
    return Converter()


def test_basic_python_types(converter):
    """Test identity conversion for basic Python types."""
    for value in [123, 12.5, "text", True]:
        assert converter(value) == value


def test_list_and_dict_conversion(converter):
    """Test identity conversion of nested lists and dictionaries."""
    input_data = {"a": [1, 2, {"b": "text"}], "c": True}
    assert converter(input_data) == input_data


def test_nested_numpy_structures(converter):
    """Test nested structures with NumPy types."""
    converter.register_numpy_types()

    obj = {
        "arr": np.array([1, 2, 3]),
        "nested": {"scalar": np.int64(42), "float": np.float32(3.1)},
    }

    expected = {
        "arr": [1, 2, 3],
        "nested": {
            "scalar": 42,
            "float": 3.1,
        },
    }

    assert compare_nested_dicts_or_lists(converter(obj), expected)


def test_register_custom_type(converter):
    """Test custom type registration and conversion."""

    class Custom:
        """Custom class for testing."""

        def __init__(self, value):
            self.value = value

    class Custom2:
        """Another custom class for testing."""

        def __init__(self, value):
            self.value = value

    def convert_custom(converter, obj):
        """Custom conversion function for the Custom class."""
        return {"custom_value": converter(obj.value)}

    converter.register_type(Custom, convert_custom)
    converter.register_type(Custom2, convert_custom)

    custom_obj = Custom2([Custom("ab"), Custom(3)])
    assert converter(custom_obj) == {
        "custom_value": [{"custom_value": "ab"}, {"custom_value": 3}]
    }


def test_not_convertible_type(converter):
    """Test conversion of a non-convertible type."""

    # register a type to enable conversion
    converter.register_numpy_types()

    class UnknownType:
        """Unknown type for testing."""

        pass

    with pytest.raises(TypeError, match=r"can not be converted"):
        converter(UnknownType())
