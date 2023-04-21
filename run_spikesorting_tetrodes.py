# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:02:41 2023 by Guido Meijer
"""

import os
import numpy as np
from datetime import datetime
from probeinterface import generate_tetrode, ProbeGroup
import spikeinterface.extractors as se
from spikeinterface.sorters import run_sorter

# Set data path 
OE_PATH = 'C:\\Users\\Neuropixel\\Documents\\Jasmin\\ML8B1_P22_s1_2023-02-27_10-37-42_maze + sleep\\Record Node 101'

# Load in recording
rec = se.read_openephys(OE_PATH)

# Add channel locations
probegroup = ProbeGroup()
for i in range(8):
    tetrode = generate_tetrode()
    tetrode.move([i * 50, 0])
    probegroup.add_probe(tetrode)
probegroup.set_global_device_channel_indices(np.arange(32))
rec.set_probegroup(probegroup, in_place=True)

# Add pandas as workaround
#rec.extra_requirements.append('pandas')
#rec.extra_requirements.append('scikit-learn')

# Start sorting
datetime.now().strftime('Starting spike sorting at %H:%M')
sort = run_sorter('mountainsort4',
                  rec,
                  output_folder=os.path.join(OE_PATH, 'experiment1', 'recording1', 'mountainsort'),
                  verbose=True,
                  docker_image=True)

            

        
         
         
         
  
