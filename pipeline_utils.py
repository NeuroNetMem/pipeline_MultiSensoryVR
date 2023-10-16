# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 10:39:03 2023

@author: Neuropixel
"""

import ibllib.io.session_params as sess_params


def create_session_description(session_path, save=True):
    """
    From a session create a dictionary corresponding to the acquisition description.

    Parameters
    ----------
    session_path : str, pathlib.Path
        A path to a session to describe.
    save : bool
        If true, saves the acquisition description file to _ibl_experiment.description.yaml.

    Returns
    -------
    dict
        The legacy acquisition description.
    """
    dict_ad = get_acquisition_description()
    if save:
        sess_params.write_params(session_path=session_path, data=dict_ad)
    return dict_ad


def get_acquisition_description():
    """
    """
   
    devices = {
        'neuropixel': {
            'probe00': {'collection': 'raw_ephys_data/probe00', 'sync_label': 'imec_sync'},
            'probe01': {'collection': 'raw_ephys_data/probe01', 'sync_label': 'imec_sync'}
        },
    }
    acquisition_description = {  # this is the current ephys pipeline description
        'devices': devices,
        'sync': {
            'nidq': {'collection': 'raw_ephys_data', 'extension': 'bin', 'acquisition_software': 'spikeglx'}
        },
        'procedures': ['Ephys recording with acute probe(s)']
    }
  
    key = 'multiSensoryVR'
     
    acquisition_description['tasks'] = [{key: {
        'collection': 'raw_behavior_data',
        'sync_label': 'bpod', 'main': True  
    }}]
    acquisition_description['version'] = '1.0.0'
    return acquisition_description