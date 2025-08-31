# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from glob import glob
import importlib.util

from typing import Dict
from .types import InputData

available: Dict[str, InputData] = {}
"""Dynamically generated dictionary of all defined inputs"""


for file_path in glob(f"{__file__.removesuffix('__init__.py')}/inputs/*.py"):
    if (
        not file_path.endswith("__init__.py")
        and not file_path.endswith("types.py")
        and not file_path.endswith("utils.py")
        and not file_path.endswith("version.py")
        and "test_" not in file_path
    ):
        module_name = (
            "fediverse_pasture_inputs.inputs." + file_path.split(".")[0].split("/")[-1]
        )

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not load spec for {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        available_name = module.data.filename.removesuffix(".md")

        if available_name in available:
            raise ValueError(f"Duplicate input data filename: {available_name}")

        available[available_name] = module.data
