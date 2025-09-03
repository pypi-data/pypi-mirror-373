"""
tests for example scripts



"""

# -----------------------------------------------------------------------------
# Copyright (c) ytree development team. All rights reserved.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# -----------------------------------------------------------------------------

from ytree.testing.example_script_test import ExampleScriptTest
from ytree.testing.utilities import TempDirTest


class TestPlotMostMassive(TempDirTest, ExampleScriptTest):
    script_filename = "plot_most_massive.py"
    input_filename = "tiny_ctrees/locations.dat"
    output_files = ("most_massive.png",)


class TestPlotMostHalos(TempDirTest, ExampleScriptTest):
    script_filename = "plot_most_halos.py"
    input_filename = "tiny_ctrees/locations.dat"
    output_files = ("most_halos.png",)
