#!/usr/bin/env python
"""
This `version` module contains the version information for the VTKio package.

Created at 12:47, 23 Feb, 2025
"""

__author__ = 'J.P. Morrissey'
__copyright__ = 'Copyright 2022-2025'
__maintainer__ = 'J.P. Morrissey'
__email__ = 'morrissey.jp@gmail.com'
__status__ = 'Development'

# Standard Library


# Imports


# Local Sources


__all__ = ['VERSION', 'version_info', 'version_short']

import vtkio.utilities

VERSION = '0.1.0.dev6'
"""The version of VTKio."""

def version_short() -> str:
    """Return the `major.minor` part of package version.

    It returns '0.2' if VTKio version is '0.2.2'.
    """
    return '.'.join(VERSION.split('.')[:2])


def version_info() -> str:
    """Return complete version information for VTKio and its dependencies."""
    import importlib.metadata as importlib_metadata
    import os
    import platform
    import sys
    from pathlib import Path

    # Local Sources


    import vtkio as vtkio


    # get data about packages that are closely related to or are used by VTKio
    package_names = {
        'h5py',
        'xmltodict',
        'numpy',
        'pybase64',
    }
    related_packages = []

    for dist in importlib_metadata.distributions():
        name = dist.metadata['Name']
        if name in package_names:
            related_packages.append(f'{name}-{dist.version}')

    vtkio_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    most_recent_commit = (
        vtkio.utilities.git_revision(vtkio_dir) if vtkio.utilities.is_git_repo(vtkio_dir) and vtkio.utilities.have_git() else 'unknown'
    )

    info = {
        'vtkio version': VERSION,
        'vtkio-core build': getattr(vtkio, 'build_info', None) or vtkio.build_profile,
        'install path': Path(__file__).resolve().parent,
        'python version': sys.version,
        'platform': platform.platform(),
        'related packages': ' '.join(related_packages),
        'commit': most_recent_commit,
    }
    return '\n'.join('{:>30} {}'.format(k + ':', str(v).replace('\n', ' ')) for k, v in info.items())