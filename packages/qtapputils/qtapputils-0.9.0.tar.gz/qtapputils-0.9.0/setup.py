# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of qtapputils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""Installation script """

import setuptools
from setuptools import setup
from qtapputils import __version__, __project_url__

LONG_DESCRIPTION = ("The qtapputils module provides various utilities "
                    "for building Qt applications in Python.")


INSTALL_REQUIRES = [
    'qtpy',
    'pyqt5',
    'matplotlib',
    'qtawesome'
    ]


setup(name='qtapputils',
      version=__version__,
      description=("Utilities for building Qt applications in Python."),
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      license='MIT',
      author='Jean-Sébastien Gosselin',
      author_email='jean-sebastien.gosselin@outlook.ca',
      url=__project_url__,
      ext_modules=[],
      packages=setuptools.find_packages(),
      package_data={},
      include_package_data=True,
      extras_require={'with-deps': INSTALL_REQUIRES},
      classifiers=["Programming Language :: Python :: 3",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent"],
      )
