# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:02:41 2023 by Guido Meijer
"""

import os
import time
import numpy as np
from datetime import datetime
from probeinterface import generate_tetrode, ProbeGroup
import spikeinterface.full as si
from spikeinterface.sorters import run_sorter

# Set data path 
OE_PATH = 'C:\\Users\\Neuropixel\\Documents\\Jasmin\\ML8B1_P22_s1_2023-02-27_10-37-42_maze + sleep\\Record Node 101'
output_path = os.path.join(OE_PATH, 'experiment1', 'recording1', 'mountainsort')

# Load in recording
rec = si.read_openephys(OE_PATH)

# Add channel locations
probegroup = ProbeGroup()
for i in range(8):
    tetrode = generate_tetrode()
    tetrode.move([i * 50, 0])
    probegroup.add_probe(tetrode)
probegroup.set_global_device_channel_indices(np.arange(32))
rec.set_probegroup(probegroup, in_place=True)

# %% Pre-processing
rec = si.bandpass_filter(rec, freq_min=300, freq_max=6000)
rec = si.common_reference(rec, operator='median', reference='global')

# %% Run spike sorting
print(f'Starting spike sorting at {datetime.now().strftime("%H:%M")}')
start = time.time()
sort = run_sorter('mountainsort4', rec, output_folder=output_path, verbose=True, docker_image=True)
end = time.time()
print(f'Done with spike sorting! At {datetime.now().strftime("%H:%M")}')
print(f'Elapsed time: {np.floor((end - start) / 60 / 60).astype(int)} hours '
      f'and {np.mod(np.round((end - start) / 60), 60).astype(int)} minutes')

# %% Post processing
print(f'\nStarting post-processing at {datetime.now().strftime("%H:%M")}')
start = time.time()

# Extract waveforms
we = si.extract_waveforms(rec, sort, os.path.join(output_path, 'waveforms'), ms_before=1.5, ms_after=2)

# Compute unit quality metrics
si.compute_principal_components(we, n_components=3, mode='by_channel_local', whiten=True)
si.compute_template_similarity(we,  method='cosine_similarity')
si.compute_spike_amplitudes(we)
si.compute_unit_locations(we)
si.compute_correlograms(we)
si.compute_quality_metrics(we, metric_names=[
    'snr', 'isi_violation', 'presence_ratio', 'isolation_distance', 'firing_rate', 'l_ratio',
    'amplitude_cutoff'])

# Export to phy
si.export_to_phy(we, output_folder=os.path.join(output_path, 'phy'))

end = time.time()
print(f'Done! At {datetime.now().strftime("%H:%M")}')
print(f'Elapsed time: {np.floor((end - start) / 60 / 60).astype(int)} hours '
      f'and {np.mod(np.round((end - start) / 60), 60).astype(int)} minutes')

         
         
         
  
