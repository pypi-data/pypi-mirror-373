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
"""Test node reader and writer."""

import pytest

from fourcipp.legacy_io.node import read_node, write_node


@pytest.mark.parametrize(
    "node_line",
    [
        "NODE 5 COORD 0.0 0.1 0.2",
        "CP 5 COORD 0.0 0.1 0.2 0.3",
        "FNODE 5 COORD 0.0 0.1 0.2 CIR 1.1 1.2 1.3 TAN 1.1 1.2 1.3 RAD 1.1 1.2 1.3 HELIX 1.4 TRANS 1.4 FIBER1 1.1 1.2 1.3 FIBER2 1.1 1.2 1.3",
    ],
)
def test_node_read_and_write(node_line):
    """Test nodes read and write."""
    assert node_line.split() == write_node(read_node(node_line)).split()


def test_unknown_node_read():
    """Test unknown node read."""
    unknown_node = "NOPE 5 COORD 0.0 0.1 0.2"
    with pytest.raises(ValueError, match="Unknown node type"):
        read_node(unknown_node)


def test_unknown_node_write():
    """Test unknown node write."""
    unknown_node = {"id": 5, "COORD": [0.0, 0.1, 0.2], "data": {"type": "NOPE"}}
    with pytest.raises(ValueError, match="Unknown node type"):
        write_node(unknown_node)
