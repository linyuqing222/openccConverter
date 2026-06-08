# -*- coding: utf-8 -*-
# Test configuration for openccConverter.
# This file is covered by the GNU General Public License, version 2 or later.

"""Make the NVDA-independent conversion core importable for the test suite.

The core module lives inside the add-on package, but it is written so that it
can be imported as a stand-alone top-level module (it does not import NVDA and
adds its own bundled engine to ``sys.path``).  We add the package directory to
``sys.path`` so ``import opencc_core`` works without NVDA being present.
"""

import os
import sys

_CORE_DIR = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	"..",
	"addon",
	"globalPlugins",
	"openccConverter",
)
sys.path.insert(0, os.path.abspath(_CORE_DIR))
