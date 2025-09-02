"""Command line interface useful for testing, forwards to cmdline."""

__author__ = "Jerome Lecomte"
__license__ = "MIT"

import sys

from finquotes import cmdline

if __name__ == "__main__":
    cmdline.main(sys.argv[1:])  # pylint: disable=no-value-for-parameter
