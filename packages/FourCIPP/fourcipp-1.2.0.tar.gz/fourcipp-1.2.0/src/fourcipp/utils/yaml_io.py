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
"""YAML io."""

import json
import pathlib
import re

import ryml

from fourcipp.utils.typing import Path


def load_yaml(path_to_yaml_file: Path) -> dict:
    """Load yaml files.

    rapidyaml is the fastest yaml parsing library we could find. Since it returns custom objects we
    use the library to emit the objects to json and subsequently read it in using the json library.
    This is still two orders of magnitude faster compared to other yaml libraries.

    Args:
        path_to_yaml_file: Path to yaml file

    Returns:
       Loaded data
    """

    json_str = ryml.emit_json(
        ryml.parse_in_arena(pathlib.Path(path_to_yaml_file).read_bytes())
    )

    # Convert `inf` to a string to avoid JSON parsing errors, see https://github.com/biojppm/rapidyaml/issues/312
    json_str = re.sub(r":\s*(-?)inf\b", r': "\1inf"', json_str)

    # Convert floats that are missing digits on either side of the decimal point
    # so .5 to 0.5 and 5. to 5.0
    json_str = re.sub(r":\s*(-?)\.([0-9]+)", r": \g<1>0.\2", json_str)
    json_str = re.sub(r":\s*(-?)([0-9]+)\.(\D)", r": \1\2.0\3", json_str)

    data = json.loads(json_str)

    return data


def dict_to_yaml_string(data: dict, sort_keys: bool = False) -> str:
    """Dump dict as yaml.

    Args:
        data: Data to dump.
        sort_keys: If true sort the sections by section name
    """

    # Sort keys
    if sort_keys:
        data = {key: data[key] for key in sorted(data.keys())}

    # Convert dictionary into a ryml tree
    tree = ryml.parse_in_arena(bytearray(json.dumps(data).encode("utf8")))

    # remove all style bits to enable a YAML style output
    # see https://github.com/biojppm/rapidyaml/issues/520
    for node_id, _ in ryml.walk(tree):
        if tree.is_map(node_id) or tree.is_seq(node_id):
            tree.set_container_style(node_id, ryml.NOTYPE)

        if tree.has_key(node_id):
            tree.set_key_style(node_id, ryml.NOTYPE)

    return ryml.emit_yaml(tree)


def dump_yaml(data: dict, path_to_yaml_file: Path, sort_keys: bool = False) -> None:
    """Dump yaml to file.

    Args:
        data: Data to dump.
        path_to_yaml_file: Yaml file path
        sort_keys: If true sort the sections by section name
    """
    pathlib.Path(path_to_yaml_file).write_text(
        dict_to_yaml_string(data, sort_keys), encoding="utf-8"
    )
