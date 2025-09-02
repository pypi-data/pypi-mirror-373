# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Provides a Generic code integration wrapper and utilities for SCADE."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata
from pathlib import Path
import sys

try:
    __version__ = importlib_metadata.version(__name__.replace('.', '-'))
except (importlib_metadata.PackageNotFoundError, AttributeError):
    # Handle the case where version cannot be determined
    __version__ = '0.0.0'


def get_srg_name() -> str:
    """
    Return the name of the registration file for Ansys SCADE IDE.

    It addresses SCADE 2024 R2 and prior releases.
    SCADE 2025 R1 and above use the package's
    ``ansys.scade.registry`` entry point.
    """
    # registrations depending on Python interpreter
    python_version = str(sys.version_info.major) + str(sys.version_info.minor)
    suffix = '23r1' if python_version == '37' else '24r2'
    return 'wux%s.srg' % suffix


def srg() -> str:
    r"""
    Return the path of the SCADE Studio registry file.

    This function implements the entry point "ansys.scade.registry/srg"
    introduced in SCADE 2025 R1. It avoids creating an explicit srg file
    in ``%APPDATA%\Scade\Customize`` when the package is installed.
    """
    # the package's srg file is located in the same directory
    return str(Path(__file__).parent / 'wux.srg')
