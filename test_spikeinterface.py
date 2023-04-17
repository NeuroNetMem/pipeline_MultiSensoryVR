# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 14:13:14 2023

@author: Neuropixel
"""

from pathlib import Path
import spikeinterface as si  # import core only
import spikeinterface.extractors as se
import spikeinterface.preprocessing as spre
import spikeinterface.sorters as ss
import spikeinterface.postprocessing as spost
import spikeinterface.qualitymetrics as sqm
import spikeinterface.comparison as sc
import spikeinterface.exporters as sexp
import spikeinterface.curation as scur
import spikeinterface.widgets as sw
from spikeinterface.sorters import run_sorter, get_default_sorter_params
import probeinterface as pi

"""
bin_path = 'C:\SGL_DATA\myRun_g0\myRun_g0_imec0'
output_path = 'C:\SGL_DATA\myRun_g0\myRun_g0_imec0\kilosort'

rec = se.read_spikeglx(bin_path, stream_id='imec0.ap')

rec = spre.highpass_filter(rec)
rec = spre.phase_shift(rec)
bad_channel_ids, all_channels = spre.detect_bad_channels(rec)
rec = spre.interpolate_bad_channels(rec, bad_channel_ids)
rec = spre.highpass_spatial_filter(rec)

fs = rec.get_sampling_frequency()
num_chan = rec.get_num_channels()
print('Sampling frequency:', fs)
print('Number of channels:', num_chan)

print('Installed sorters', ss.installed_sorters())

rec = run_sorter('pykilosort', rec, output_folder=output_path,
                 preprocessing_function='destriping', verbose=True,
                 docker_image=True)

#recording = run_sorter('pykilosort', recording)

#recording = run_sorter('kilosort3', recording, output_folder=output_path,
#                       docker_image=True, verbose=True)
"""
chan_path = 'C:\\Users\\Neuropixel\\Documents\\Kilosort\\Kilosort-2.5_preprocess_files\\neuropixPhase3B1_kilosortChanMap.mat'

oe_path = 'K:\\NeuropixelData\\426993\\426993-20220506'
output_path = 'K:\\SpikeSortingTest\\426993-20220506'

rec = se.read_openephys(oe_path, stream_id='1')

rec.set_channel_locations(channel_locs)



bad_channel_ids, all_channels = spre.detect_bad_channels(rec)

rec = run_sorter('kilosort3', rec, output_folder=output_path, verbose=True,
                 docker_image=True)




