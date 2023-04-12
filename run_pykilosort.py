# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:02:41 2023 by Guido Meijer
"""

import os
from pykilosort.ibl import run_spike_sorting_ibl, ibl_pykilosort_params, download_test_data

DATA_FOLDER = 'K:\\NeuropixelData'

# Search for spikesort_me.flag
for root, directory, files in os.walk(DATA_FOLDER):
     if 'spikesort_me.flag' in files:
         print(f'Start spikesorting session {root}')
         
         
  
