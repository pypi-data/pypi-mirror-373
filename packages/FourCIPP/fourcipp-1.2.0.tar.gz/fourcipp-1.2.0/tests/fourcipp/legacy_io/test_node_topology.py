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
"""Test node topology io."""

import pytest

from fourcipp.legacy_io.node_topology import (
    read_node_topology,
    write_node_topology,
)


@pytest.mark.parametrize(
    "line",
    [
        "NODE 9 DNODE 1",
        "NODE 9 DLINE 1",
        "NODE 9 DSURFACE 1",
        "NODE 9 DVOL 1",
    ],
)
def test_dtopology_read_and_write(line):
    """Test DNODE, DLINE, DSURFACE, DVOL read and write."""
    assert line.split() == write_node_topology(read_node_topology(line)).split()


@pytest.mark.parametrize(
    "line",
    [
        "CORNER fluid x- y- z+ DNODE 1",
        "EDGE fluid y+ y- DLINE 1",
        "SIDE fluid y+ DSURFACE 1",
        "VOLUME fluid DVOL 1",
    ],
)
def test_domain_read_and_write(line):
    """Test CORNER, EDGE, SIDE, VOLUME read and write."""
    assert line.split() == write_node_topology(read_node_topology(line)).split()


def test_read_node_topology_error():
    """Test node topology error."""
    unknown_node = "NOPE something"
    with pytest.raises(ValueError, match="Unknown type"):
        read_node_topology(unknown_node)
