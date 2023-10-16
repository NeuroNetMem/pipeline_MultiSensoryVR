# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:02:41 2023 by Guido Meijer
"""

import os
from os.path import join, split, isfile
import numpy as np
from datetime import datetime
import shutil
from glob import glob
from pathlib import Path
import json

from ibllib.ephys import ephysqc
from ibllib.pipes.ephys_tasks import (EphysCompressNP1, EphysSyncPulses, EphysSyncRegisterRaw,
                                      EphysPulses)
from ibllib.ephys.spikes import ks2_to_alf, sync_spike_sorting

import spikeinterface.extractors as se
import spikeinterface.preprocessing as spre
from spikeinterface.sorters import run_sorter
from spikeinterface.core import extract_waveforms
from spikeinterface.postprocessing import compute_spike_amplitudes, compute_correlograms
from spikeinterface.qualitymetrics import compute_quality_metrics
from spikeinterface.exporters import export_report

import matlab.engine


# Set data path
SPIKE_SORTER = 'kilosort2_5'  
IDENTIFIER = ''  # will be appended to SPIKE_SORTER when saving 
DATA_FOLDER = 'D:\\NeuropixelData'
BOMBCELL_PATH = 'C:\\Users\\Neuropixel\\Documents\\MATLAB\\bombcell'
MATLAB_NPY_PATH = 'C:\\Users\\Neuropixel\\Documents\\MATLAB\\npy-matlab\\npy-matlab'

# Set sync channel
nidq_sync_dictionary = {
    "SYSTEM": "3B",
    "SYNC_WIRING_DIGITAL": {
        "P0.0": "barcode",
        "P0.3": "imec_sync",
    },
}

probe_sync_dictionary = {
    "SYSTEM": "3B",
    "SYNC_WIRING_DIGITAL": {
        "P0.6": "imec_sync"
    }
}

# Initialize Matlab engine for bombcell package
eng = matlab.engine.start_matlab()
eng.addpath(r"{}".format(os.path.dirname(os.path.realpath(__file__))), nargout=0)
eng.addpath(eng.genpath(BOMBCELL_PATH))
eng.addpath(MATLAB_NPY_PATH)

# Search for spikesort_me.flag
print('Looking for spikesort_me.flag..')
for root, directory, files in os.walk(DATA_FOLDER):
    if 'spikesort_me.flag' in files:
        session_path = Path(root)
        print(f'\nFound spikesort_me.flag in {root}')
        
        # Restructure file and folders
        if 'probe00' not in os.listdir(join(root, 'raw_ephys_data')):
            if len(os.listdir(join(root, 'raw_ephys_data'))) == 0:
                print('No ephys data found')
                continue
            elif len(os.listdir(join(root, 'raw_ephys_data'))) > 1:
                print('More than one run found, not supported')
                continue
            orig_dir = os.listdir(join(root, 'raw_ephys_data'))[0]
            for i, this_dir in enumerate(os.listdir(join(root, 'raw_ephys_data', orig_dir))):
                shutil.move(join(root, 'raw_ephys_data', orig_dir, this_dir),
                            join(root, 'raw_ephys_data'))
            os.rmdir(join(root, 'raw_ephys_data', orig_dir))
            for i, this_path in enumerate(glob(join(root, 'raw_ephys_data', '*imec*'))):
                os.rename(this_path, join(root, 'raw_ephys_data', 'probe0' + this_path[-1]))
                
        # Create synchronization file
        nidq_file = next(session_path.joinpath('raw_ephys_data').glob('*.nidq.*bin'))
        with open(nidq_file.with_suffix('.wiring.json'), 'w') as fp:
            json.dump(nidq_sync_dictionary, fp, indent=1)
        
        for ap_file in session_path.joinpath('raw_ephys_data').rglob('*.ap.cbin'):
            with open(ap_file.with_suffix('.wiring.json'), 'w') as fp:
                json.dump(probe_sync_dictionary, fp, indent=1)
        
        # Create nidq sync file
        EphysSyncRegisterRaw(session_path=session_path, sync_collection='raw_ephys_data').run()
                
        probes = glob(join(root, 'raw_ephys_data', 'probe*'))
        for i, this_probe in enumerate(probes):
             
            # Compress raw data
            print('Compressing raw binary file')
            if len(glob(join(root, 'raw_ephys_data', this_probe[-7:], '*ap.cbin'))) == 0:
                task = EphysCompressNP1(session_path=Path(root), pname=this_probe[-7:])
                task.run()
                        
            # Create probe sync file
            task = EphysSyncPulses(session_path=session_path, sync='nidq', pname=this_probe[-7:],
                                   sync_ext='bin', sync_namespace='spikeglx',
                                   sync_collection='raw_ephys_data',
                                   device_collection='raw_ephys_data')
            task.run()
            task = EphysPulses(session_path=session_path, pname=this_probe[-7:],
                               sync_collection='raw_ephys_data',
                               device_collection='raw_ephys_data')
            task.run()
            
            # Compute raw ephys QC metrics
            #task = ephysqc.EphysQC('', session_path=session_path, use_alyx=False)
            #task.probe_path = Path(this_probe)
            #task.run()
            
            # Load in recording            
            rec = se.read_spikeglx(this_probe, stream_id=f'imec{split(this_probe)[-1][-1]}.ap')
                                    
            # Pre-process 
            rec = spre.highpass_filter(rec)
            rec = spre.phase_shift(rec)
            bad_channel_ids, all_channels = spre.detect_bad_channels(rec)
            rec = spre.interpolate_bad_channels(rec, bad_channel_ids)
            rec = spre.highpass_spatial_filter(rec)
            #rec = spre.correct_motion(rec)
                
            # Run spike sorting
            try:
                print(f'Starting {split(this_probe)[-1]} spike sorting at {datetime.now().strftime("%H:%M")}')
                #sort = run_sorter(SPIKE_SORTER, rec,
                #                  output_folder=os.path.join(this_probe, SPIKE_SORTER + IDENTIFIER),
                #                  verbose=True, docker_image=True)
            except Exception as err:
                print(err)
                
                # Log error to disk
                logf = open(os.path.join(this_probe, 'error_log.txt'), 'w')
                logf.write(str(err))
                logf.close()
                
                # Continue with next recording
                continue
            
            """
            # Export to phy
            we = extract_waveforms(rec, sort,
                                   os.path.join(this_probe, SPIKE_SORTER + IDENTIFIER, 'sorter_output', 'waveforms'),
                                   sparse=True)
            
            # some computations are done before to control all options
            compute_spike_amplitudes(we)
            compute_correlograms(we)
            compute_quality_metrics(we, metric_names=['snr', 'isi_violation', 'presence_ratio'])
            export_report(we, output_folder=os.path.join(this_probe, SPIKE_SORTER + IDENTIFIER, 'sorter_report'))
            """
            
            # Run Bombcell
            orig_ap_file = glob(join(root, 'raw_ephys_data', this_probe[-7:], '*ap.bin'))
            meta_file = glob(join(root, 'raw_ephys_data', this_probe[-7:], '*ap.meta'))
            print('Running Bombcell')
            eng.run_bombcell(join(this_probe, SPIKE_SORTER + IDENTIFIER, 'sorter_output'),
                             orig_ap_file[0],
                             meta_file[0],  
                             join(this_probe, SPIKE_SORTER+IDENTIFIER, 'bombcell_qc'),
                             this_probe,
                             nargout=0)
            
            # Delete copied recording.dat file
            if isfile(join(this_probe, SPIKE_SORTER+IDENTIFIER, 'sorter_output', 'recording.dat')):
                os.remove(join(this_probe, SPIKE_SORTER+IDENTIFIER, 'sorter_output', 'recording.dat'))
                
            # Delete original raw data
            orig_ap_file = glob(join(root, 'raw_ephys_data', this_probe[-7:], '*ap.bin'))
            if len(orig_ap_file) == 1:
                os.remove(orig_ap_file[0])
            
            # Export spike sorting to alf files
            os.mkdir(join(root, 'alf'))
            os.mkdir(join(root, 'alf', this_probe[-7:]))
            ks2_to_alf(Path(join(this_probe, SPIKE_SORTER+IDENTIFIER, 'sorter_output')),
                       Path(join(root, 'raw_ephys_data', this_probe[-7:])),
                       Path(join(root, 'alf', this_probe[-7:])))
            
            # Synchronize spike sorting to nidq clock
            ap_file = glob(join(root, 'raw_ephys_data', this_probe[-7:], '*ap.cbin'))[0]
            sync_spike_sorting(Path(ap_file), Path(join(root, 'alf', this_probe[-7:])))
            
            print(f'Done! At {datetime.now().strftime("%H:%M")}')
        
        
        # Delete spikesort_me.flag
        #os.remove(os.path.join(root, 'spikesort_me.flag'))
             
            
            
            
            
            
        
        
         
         
         
  
