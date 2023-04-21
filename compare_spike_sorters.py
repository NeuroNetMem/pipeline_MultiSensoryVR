# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 11:13:50 2023

@author: Neuropixel
"""

import spikeinterface.extractors as se
import spikeinterface.comparison as sc
import spikeinterface.widgets as sw

sorter_1 = 'D:\\NeuropixelData\\Recday5_a7_2022-12-12_14-42-44\\Record_Node_105\\experiment1\\recording2\\continuous\\Neuropix-PXI-111.0\\pykilosort\\sorter_output\\output'
sorter_2 = 'D:\\NeuropixelData\\Recday5_a7_2022-12-12_14-42-44\\Record_Node_105\\experiment1\\recording2\\continuous\\Neuropix-PXI-111.0\\kilosort2_5\\sorter_output'
sorter_3 = 'D:\\NeuropixelData\\Recday5_a7_2022-12-12_14-42-44\\Record_Node_105\\experiment1\\recording2\\continuous\\Neuropix-PXI-111.0\\kilosort3\\sorter_output'

pykilosort = se.read_kilosort(sorter_1)
kilosort2_5 = se.read_kilosort(sorter_2)
kilosort3 = se.read_kilosort(sorter_3)

print(f'pykilosort: {pykilosort.unit_ids.shape[0]} units')
print(f'kilosort 2.5: {kilosort2_5.unit_ids.shape[0]} units')
print(f'kilosort 3: {kilosort3.unit_ids.shape[0]} units')