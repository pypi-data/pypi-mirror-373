from __future__ import annotations

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Mapping, Optional, Union

from setuptools import build_meta as orig_build_meta

# https://setuptools.pypa.io/en/latest/build_meta.html#dynamic-build-dependencies-and-other-build-meta-tweaks
# ... It is important to import * so that the hooks that you choose not to reimplement would be
# inherited from the setuptools’ backend automatically. This will also cover hooks that might
# be added in the future...
# pyright: reportWildcardImportFromLibrary=false
# pylint: disable=wildcard-import,unused-wildcard-import
from setuptools.build_meta import *


SLICE_SUFFIX = ".ice"


class BackendError(Exception):
    pass


ConfigSettings = Mapping[str, Union[str, List[str]]]


def get_requires_for_build_wheel(config_settings: Optional[ConfigSettings] = None) -> List[str]:
    # pylint: disable=function-redefined
    result = orig_build_meta.get_requires_for_build_wheel(config_settings=config_settings)
    result.append("zeroc-ice")
    return result


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[ConfigSettings] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    # pylint: disable=function-redefined

    # Ensure there is exactly one package directory (slice files storage package).
    _root, dirs, _files = next(os.walk(".", topdown=True))
    dirs = [d for d in dirs if (Path(".") / d / "__init__.py").exists()]
    if len(dirs) == 0:
        raise BackendError("Can't find package directory (slice files storage package)")
    if len(dirs) > 1:
        raise BackendError("Multiple package directories found while expected one (slice files storage package)")
    slice_storage_pkg_name = dirs[0]

    slice_pkg_dir = Path(".") / slice_storage_pkg_name
    slice_files_rel_paths = [p.relative_to(slice_pkg_dir) for p in slice_pkg_dir.glob(f"**/*{SLICE_SUFFIX}")]
    subprocess_cwd = slice_pkg_dir
    subprocess_output_dir = ".."

    # Use --underscore option to permit underscores in the Slice:
    # https://forums.zeroc.com/discussion/5923/slice-illegal-underscore-in-identifier
    args: list[str] = f"{sys.executable} -m slice2py --underscore -I. --output-dir {subprocess_output_dir}".split()
    args += [str(rel_path) for rel_path in slice_files_rel_paths]
    completed = subprocess.run(args, cwd=subprocess_cwd, check=False)
    if completed.returncode != 0:
        raise BackendError(f"Command {args} failed with code {completed.returncode}")

    # Call original setuptools function.
    return orig_build_meta.build_wheel(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory,
    )
