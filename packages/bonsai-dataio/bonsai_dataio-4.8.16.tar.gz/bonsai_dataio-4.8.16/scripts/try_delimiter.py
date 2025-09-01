"""Experiment with delimiter"""

import pandas as pd

from dataio import datapackage as iodp

"""
iodp.describe('data/delimiter/delimiter.dataio.yaml',
              overwrite=True,
              log_name='describe.log')
"""
"""
iodp.validate('data/delimiter/delimiter.dataio.yaml',
              overwrite=True,
              log_name='validate.log')
"""

df = iodp.plot("data/delimiter/delimiter.dataio.yaml")
