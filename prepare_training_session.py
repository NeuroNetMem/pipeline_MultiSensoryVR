# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 11:01:06 2023

@author: Guido Meijer
"""

from os import mkdir
from os.path import join, isdir, isfile
from datetime import date


# Set path to save data
PATH = 'K:\\Subjects'

# Get date of today
this_date = date.today().strftime('%Y%m%d')

# Get mouse name
subject_name = input('Subject name (q to quit): ')

while subject_name != 'q':
        
    # Make directories
    while not isdir(join(PATH, subject_name)):
        if not isdir(join(PATH, subject_name)):
            create_folder = input('Subject does not exist, create subject folder? (y/n) ')
            if create_folder == 'y':        
                mkdir(join(PATH, subject_name))
            else:
                subject_name = input('Subject name (q to quit): ')
            
    if not isdir(join(PATH, subject_name, this_date)):
        mkdir(join(PATH, subject_name, this_date))
        mkdir(join(PATH, subject_name, this_date, 'raw_behavior_data'))
        mkdir(join(PATH, subject_name, this_date, 'raw_video_data'))
        print(f'Created session {this_date} for {subject_name}')
        
    # Create extraction flag
    if not isfile(join(PATH, subject_name, this_date, 'extract_me.flag')):
        with open(join(PATH, subject_name, this_date, 'extract_me.flag'), 'w') as fp:
            pass
        
    # Create transfer flag
    if not isfile(join(PATH, subject_name, this_date, 'transfer_me.flag')):
        with open(join(PATH, subject_name, this_date, 'transfer_me.flag'), 'w') as fp:
            pass
    
    # Get mouse name
    subject_name = input('Subject name (q to quit): ')
            

    

