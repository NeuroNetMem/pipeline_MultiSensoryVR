# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 15:08:20 2023

@author: Guido Meijer
"""

import os
from os.path import join
import numpy as np

DATA_FOLDER = 'U:\\guido\\Subjects'

# Search for spikesort_me.flag
print('Looking for extract_me.flag..')
for root, directory, files in os.walk(DATA_FOLDER):
    if 'spikeposition_me.flag' in files:
        print(f'\nFound spikeposition_me.flag in {root}')
        
        # Load in data
        spike_times = np.load(join(root, 'spikes.times.npy'))
        wheel_dist = np.load(join(root, 'continuous.distance.npy'))
        wheel_times = np.load(join(root, 'continuous.times.npy'))
        
        # Find for each spike its corresponding distance
        spike_dist = np.empty(spike_times.shape)
        for ii, spike_time in enumerate(spike_times):
            if np.mod(ii, 1000) == 0:
                print('Processed spike {ii} of {spike_times.shape[0]}')
            spike_dist[ii] = wheel_dist[np.argmin(np.abs(wheel_times - spike_time))]
        
        # Save result
        np.save(join(root, 'spikes.distances.npy'), spike_dist)
        print(f'Successfully extracted spike distances in {root}')
