#!/usr/bin/env python

import os
import sys

# Add to PYTHONPATH so absolute imports work
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from mnimi.app import app

if __name__ == "__main__":
    app()
