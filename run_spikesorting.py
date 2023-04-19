# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:02:41 2023 by Guido Meijer
"""

import os
import numpy as np
import json
from datetime import datetime
from probeinterface import Probe
import spikeinterface.extractors as se
import spikeinterface.preprocessing as spre
from spikeinterface.extractors.neuropixels_utils import get_neuropixels_sample_shifts
from spikeinterface.sorters import run_sorter

# Set data path
DATA_FOLDER = 'D:\\NeuropixelData'
SPIKE_SORTER = 'pykilosort'

# Load in channel locations (only for data collected with OpenEphys GUI < 0.6)
channel_locs = np.load('C:\\Users\\Neuropixel\\Documents\\spikeinterface\\channel_locations.npy')

# Search for spikesort_me.flag
print('Looking for spikesort_me.flag..')
for root, directory, files in os.walk(DATA_FOLDER):
    if 'spikesort_me.flag' in files:
        print(f'\nFound spikesort_me.flag in {root}')
        
        # OpenEphys recording
        if 'continuous.dat' in files:
            print('OpenEphys recording detected')
            
            # Load in recording
            split_path = root.split(os.sep)[:-5]
            oe_path = os.path.join(split_path[0] + os.sep, *split_path)
            rec = se.read_openephys(oe_path, stream_id=root[-1])
            
            # Get OpenEphys GUI version
            split_path = root.split(os.sep)[:-2]
            meta_path = os.path.join(split_path[0] + os.sep, *split_path)
            info = json.load(open(os.path.join(meta_path, 'structure.oebin'), 'r'))
            print(f'GUI version {info["GUI version"]}')
            
            # For OpenEphys GUI version < 6, we need to add the channel location information 
            if int(info['GUI version'][2]) < 6:
                
                # Add channel locations
                probe = Probe(ndim=2, si_units='um')
                probe.set_contacts(positions=channel_locs, shapes='circle', shape_params={'radius': 5})
                probe.set_device_channel_indices(np.arange(channel_locs.shape[0]))
                rec.set_probe(probe, in_place=True)
                
                # Set inter sample shift            
                inter_sample_shifts = get_neuropixels_sample_shifts(384, 12)
            
                # Correct for inter sample shifts
                rec = spre.highpass_filter(rec)
                
                # Detect and remove bad channels
                bad_channel_ids, channel_labels = spre.detect_bad_channels(rec)
                
                # Correct for inter-sample shifts
                rec = spre.phase_shift(rec, inter_sample_shift=inter_sample_shifts)

                # Do common reference to remove artifacts
                rec = spre.common_reference(rec, operator="median", reference="global")

            else:
                # Correct for inter sample shifts
                rec = spre.highpass_filter(rec)
                rec = spre.phase_shift(rec)
                
                # Detect and interpolate bad channels
                bad_channel_ids, all_channels = spre.detect_bad_channels(rec)
                rec = spre.interpolate_bad_channels(rec, bad_channel_ids)
                rec = spre.highpass_spatial_filter(rec)
       
        # SpikeGLX recording
        elif any(s.endswith('ap.bin') for s in files):
            print('SpikeGLX recording detected')
            
            # Load in recording            
            rec = se.read_spikeglx(root, stream_id=f'{root[-5:]}.ap')
            
            # Pre-process 
            rec = spre.highpass_filter(rec)
            rec = spre.phase_shift(rec)
            bad_channel_ids, all_channels = spre.detect_bad_channels(rec)
            rec = spre.interpolate_bad_channels(rec, bad_channel_ids)
            rec = spre.highpass_spatial_filter(rec)
            
        # Run Kilosort3
        try:
            datetime.now().strftime('Starting spike sorting at %H:%M')
            sort = run_sorter(SPIKE_SORTER, rec, output_folder=os.path.join(root, SPIKE_SORTER),
                              verbose=True, docker_image=True)
        except Exception as err:
            print(err)
            
            # Log error to disk
            logf = open(os.path.join(root, 'error_log.txt'), 'w')
            logf.write(str(err))
            logf.close()
            
            # Continue with next recording
            continue
        
        # Delete spikesort_me.flag
        datetime.now().strftime('Done! At %H:%M')
        os.remove(os.path.join(root, 'spikesort_me.flag'))
             
            
            
            
            
            
        
        
         
         
         
  
