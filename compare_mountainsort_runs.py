# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 11:13:50 2023

@author: Neuropixel
"""
import os
import matplotlib.pyplot as plt
import spikeinterface.full as si

# Set data path 
OE_PATH = 'C:\\Users\\Neuropixel\\Documents\\Jasmin\\ML8B1_P22_s1_2023-02-27_10-37-42_maze + sleep\\Record Node 101'
output_path = os.path.join(OE_PATH, 'experiment1', 'recording1', 'mountainsort')

# Load in recording and sorting
rec = si.read_openephys(OE_PATH)
run_1 = si.NpzSortingExtractor(os.path.join(OE_PATH, 'experiment1', 'recording1', 'mountainsort_run1', 'sorter_output', 'firings.npz'))
run_2 = si.NpzSortingExtractor(os.path.join(OE_PATH, 'experiment1', 'recording1', 'mountainsort_run3', 'sorter_output', 'firings.npz'))

cmp_HS_TDC = si.compare_two_sorters(sorting1=run_2, sorting2=run_1, sorting1_name='Run 2', sorting2_name='Run 1')

f, ax = plt.subplots(1, 1, figsize=(16, 10), dpi=100)
si.plot_agreement_matrix(cmp_HS_TDC, ax=ax)