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
"""Test yaml io utils."""

from fourcipp.utils.yaml_io import dump_yaml, load_yaml


def test_dump_not_sorted(tmp_path):
    """Test if key order is preserved."""
    data = {"c": 1, "b": 2, "a": 3}
    sorted_file_path = tmp_path / "sorted.yaml"
    dump_yaml(data, path_to_yaml_file=sorted_file_path)
    reloaded_data = load_yaml(sorted_file_path)
    assert reloaded_data == data


def test_dump_sorted(tmp_path):
    """Test if key order is sorted."""
    data = {"c": 1, "b": 2, "a": 3}
    sorted_file_path = tmp_path / "sorted.yaml"
    dump_yaml(data, path_to_yaml_file=sorted_file_path, sort_keys=True)
    reloaded_data = load_yaml(sorted_file_path)
    assert list(reloaded_data.keys()) == sorted(data.keys())
