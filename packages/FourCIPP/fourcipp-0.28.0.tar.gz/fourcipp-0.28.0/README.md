<p align="center">
  <picture>
    <img
      src="docs/assets/fourcipp_logo_black.svg"
      width="300"
      title="FourCIPP logo"
      alt="FourCIPP logo">
  </picture>
</p>

FourCIPP (**FourC** **I**nput **P**ython **P**arser) holds a Python Parser to simply interact with [4C](https://github.com/4C-multiphysics/4C) YAML input files. This tool provides a streamlined approach to data handling for third party tools.

## Overview <!-- omit from toc -->
- [Installation](#installation)
- [Quickstart example](#quickstart-example)
- [Configuration](#configuration)
- [Developing FourCIPP](#developing-fourcipp)
- [Dependency Management](#dependency-management)
- [License](#license)



## Installation

For a quick and easy start an Anaconda/Miniconda environment is highly recommended. Other ways to install FourCIPP are possible but here the installation procedure is explained based on a conda install. After installing Anaconda/Miniconda
execute the following steps:

- Create a new Anaconda environment:
  ```bash
  conda create -n fourcipp python=3.12
  ```

- Activate your newly created environment:
  ```bash
  conda activate fourcipp
  ```

- Install all requirements without fixed versions via:
  ```
  pip install .
  ```
  > Note: This is the default behavior. This allows to use fourcipp within other projects without version conflicts.

- Install all requirements with fixed versions with:
  ```
  pip install .[safe]
  ```

Now you are up and running 🎉

## Quickstart example
<!--example, do not remove this comment-->
```python
from fourcipp.fourc_input import FourCInput

# Create a new 4C input via
input_4C = FourCInput()

# Or load an existing input file
input_4C = FourCInput.from_4C_yaml(input_file_path)

# Add or overwrite sections
input_4C["PROBLEM TYPE"] = {"PROBLEMTYPE": "Structure"}
input_4C["PROBLEM SIZE"] = {"DIM": 3, "ELEMENTS": 1_000}

# Update section parameter
input_4C["PROBLEM SIZE"]["ELEMENTS"] = 1_000_000

# Add new parameter
input_4C["PROBLEM SIZE"]["NODES"] = 10_000_000

# Remove section
removed_section = input_4C.pop("PROBLEM SIZE")

# Dump to file
input_4C.dump(input_file_path, sort_sections=True, validate=True)
```
<!--example, do not remove this comment-->

## Configuration
FourCIPP utilizes the `4C_metadata.yaml` and `schema.json` files generated during the 4C build to remain up-to-date with your 4C build. By default, the files for the latest 4C input version can be found in `src/fourcipp/config`. You can add custom metadata and schema paths to the configuration file `src/fourcipp/config/config.yaml` by adding a new profile:
```yaml
profile: your_custom_files
profiles:
  your_custom_files:
    4C_metadata_path: /absolute/path/to/your/4C_metadata.yaml
    json_schema_path: /absolute/path/to/your/4C_schema.json
  default:
    4C_metadata_path: 4C_metadata.yaml
    json_schema_path: 4C_schema.json
    description: 4C metadata from the latest successful nightly 4C build
  4C_docker_main:
    4C_metadata_path: /home/user/4C/build/4C_metadata.yaml
    json_schema_path: /home/user/4C/build/4C_schema.json
    description: 4C metadata in the main 4C docker image
```
and select it using the `profile` entry.


## Developing FourCIPP

If you plan on actively developing FourCIPP it is advisable to install in editable mode with the development requirements like

```bash
pip install -e .[dev]
```

You can install the pre-commit hook with:
```
pre-commit install
```

## Dependency Management

To ease the dependency update process [`pip-tools`](https://github.com/jazzband/pip-tools) is utilized. To create the necessary [`requirements.txt`](./requirements.txt) file simply execute

```
pip-compile --all-extras --output-file=requirements.txt requirements.in
````

To upgrade the dependencies simply execute

```
pip-compile --all-extras --output-file=requirements.txt --upgrade requirements.in
````

## License

This project is licensed under a MIT license. For further information check [`LICENSE`](./LICENSE).
