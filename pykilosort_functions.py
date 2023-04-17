# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 16:17:44 2023 by Guido Meijer
"""

from pathlib import Path
import datetime
import json
import logging
import shutil

import numpy as np

import spikeglx
import neuropixel
from ibllib.ephys import spikes
from one.remote import aws
from pykilosort import add_default_handler, run, Bunch, __version__
from pykilosort.params import KilosortParams


_logger = logging.getLogger("pykilosort")


def _sample2v(ap_file):
    md = spikeglx.read_meta_data(ap_file.with_suffix(".meta"))
    s2v = spikeglx._conversion_sample2v_from_meta(md)
    return s2v["ap"][0]


def run_spike_sorting(bin_file, scratch_dir=None, delete=True,
                      ks_output_dir=None, alf_path=None, log_level='INFO', params=None):
    """
    This runs the spike sorting and outputs the raw pykilosort without ALF conversion
    :param bin_file: binary file full path
    :param scratch_dir: working directory (home of the .kilosort folder) SSD drive preferred.
    :param delete: bool, optional, defaults to True: whether or not to delete the .kilosort temp folder
    :param ks_output_dir: string or Path: output directory defaults to None, in which case it will output in the
     scratch directory.
    :param alf_path: strint or Path, optional: if specified, performs ks to ALF conversion in the specified folder
    :param log_level: string, optional, defaults to 'INFO'
    :return:
    """
    START_TIME = datetime.datetime.now()
    # handles all the paths infrastructure
    assert scratch_dir is not None
    scratch_dir.mkdir(exist_ok=True, parents=True)
    ks_output_dir = Path(ks_output_dir) if ks_output_dir is not None else scratch_dir.joinpath('output')
    log_file = scratch_dir.joinpath(f"_{START_TIME.strftime('%Y-%m-%d_%H%M')}_kilosort.log")
    add_default_handler(level=log_level)
    add_default_handler(level=log_level, filename=log_file)
    session_scratch_dir = scratch_dir.joinpath('.kilosort', bin_file.stem)
    # construct the probe geometry information
    if params is None:
        params = pykilosort_params(bin_file)
    try:
        _logger.info(f"Starting Pykilosort version {__version__}")
        _logger.info(f"Scratch dir {ks_output_dir}")
        _logger.info(f"Output dir {bin_file.parent}")
        _logger.info(f"Log file {log_file}")
        _logger.info(f"Loaded probe geometry for NP{params['probe']['neuropixel_version']}")

        run(bin_file, dir_path=scratch_dir, output_dir=ks_output_dir, **params)
        # move back the QC files to the original probe folder for registration
        for qc_file in session_scratch_dir.rglob('_iblqc_*'):
            shutil.copy(qc_file, ks_output_dir.joinpath(qc_file.name))
        if delete:
            shutil.rmtree(scratch_dir.joinpath(".kilosort"), ignore_errors=True)
    except Exception as e:
        _logger.exception("Error in the main loop")
        raise e
    [_logger.removeHandler(h) for h in _logger.handlers]
    # move the log file and all qcs to the output folder
    shutil.move(log_file, ks_output_dir.joinpath('spike_sorting_pykilosort.log'))

    # convert the pykilosort output to ALF IBL format
    if alf_path is not None:
        s2v = _sample2v(bin_file)
        alf_path.mkdir(exist_ok=True, parents=True)
        spikes.ks2_to_alf(ks_output_dir, bin_file, alf_path, ampfactor=s2v)


def pykilosort_params(bin_file):
    params = KilosortParams()
    #params.low_memory = True
    params.ntbuff = 64
    params.preprocessing_function = 'destriping'
    params.probe = probe_geometry(bin_file)
    params.minFR = 0
    params.minfr_goodchannels = 0
    # params = {k: dict(params)[k] for k in sorted(dict(params))}
    return dict(params)


def probe_geometry(bin_file):
    """
    Loads the geometry from the meta-data file of the spikeglx acquisition system
    sr: ibllib.io.spikeglx.Reader or integer with neuropixel version 1 or 2
    """
    if isinstance(bin_file, list):
        sr = spikeglx.Reader(bin_file[0])
        h, ver, s2v = (sr.geometry, sr.major_version, sr.sample2volts[0])
    elif isinstance(bin_file, str) or isinstance(bin_file, Path):
        sr = spikeglx.Reader(bin_file)
        h, ver, s2v = (sr.geometry, sr.major_version, sr.sample2volts[0])
    else:
        print(bin_file)
        assert(bin_file == 1 or bin_file == 2)
        h, ver, s2v = (neuropixel.trace_header(version=bin_file), bin_file, 2.34375e-06)
    nc = h['x'].size
    probe = Bunch()
    probe.NchanTOT = nc + 1
    probe.chanMap = np.arange(nc)
    probe.xc = h['x'] + h['shank'] * 200
    probe.yc = h['y']
    probe.x = h['x']
    probe.y = h['y']
    probe.shank = h['shank']
    probe.kcoords = np.zeros(nc)
    probe.channel_labels = np.zeros(nc, dtype=int)
    probe.sample_shift = h['sample_shift']
    probe.h, probe.neuropixel_version, probe.sample2volt = (h, ver, s2v)
    return probe

