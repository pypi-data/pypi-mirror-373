# The file config.py in various modules contains code taken from
# https://github.com/dask/dask/tree/main/dask, released under the BSD 3-Clause
# license, with copyright attributed to Anaconda Inc (2014).
# This information is also include in NOTICE.md.


"""Setup config"""

import os

import pyearthtools.utils
import yaml


def reconfigure():
    fn = os.path.join(os.path.dirname(__file__), "data.yaml")
    pyearthtools.utils.config.ensure_file(source=fn)

    with open(fn) as f:
        defaults = yaml.safe_load(f)

    pyearthtools.utils.config.update_defaults(defaults)


reconfigure()
