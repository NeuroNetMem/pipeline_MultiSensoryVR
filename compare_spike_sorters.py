# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 11:13:50 2023

@author: Neuropixel
"""

import spikeinterface.sorters as ss

sorter_1 = 'D:\\NeuropixelData\\Recday5_a7_2022-12-12_14-42-44\\Record_Node_105\\experiment1\\recording2\\continuous\\Neuropix-PXI-111.0\\pykilosort'

kilosort3 = ss.read_sorter_folder(sorter_1)