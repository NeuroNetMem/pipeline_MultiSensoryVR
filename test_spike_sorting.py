# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from pykilosort_functions import run_spike_sorting
from pathlib import Path

bin_file=Path('C:\\SGL_DATA\\myRun_g0\\myRun_g0_imec0\\myRun_g0_t0.imec0.ap.bin')
alf_path = bin_file.joinpath('alf')
scratch_dir = Path('C:\\Users\\Neuropixel\\Documents\\scratch')

run_spike_sorting(bin_file, scratch_dir=scratch_dir, alf_path=alf_path)