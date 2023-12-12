# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 15:06:13 2023

@author: Neuropixel
"""

import os
from os.path import join, split
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--ephys", help="Ephys session", action='store_true')
args = parser.parse_args()

if args.ephys:
    LOCAL_FOLDER = 'D:\\NeuropixelData'
else:
    LOCAL_FOLDER = 'K:\\Subjects'
REMOTE_FOLDER = '\\\\imaging1-srv.science.ru.nl\\imaging1\\guido\\Subjects'

# Search for transfer_me.flag
print('Looking for transfer_me.flag')
for root, directory, files in os.walk(LOCAL_FOLDER):
    if 'transfer_me.flag' in files:
        if len(os.listdir(join(root, 'raw_behavior_data'))) == 0:
            print('No behavioral data found, skipping transfer for this session')
            continue
        elif len(os.listdir(join(root, 'raw_behavior_data'))) > 0:
            print('Warning: multiple behavior files found, will transfer all')
        
        # Copy data
        print(f'\nCopying session {root} to server')
        shutil.copytree(root, join(REMOTE_FOLDER, split(split(root)[0])[1], split(root)[1]))
       
        # Delete transfer_me flags
        os.remove(join(root, 'transfer_me.flag'))
        os.remove(join(REMOTE_FOLDER, split(split(root)[0])[1], split(root)[1], 'transfer_me.flag'))
        print('Done!')
        
        