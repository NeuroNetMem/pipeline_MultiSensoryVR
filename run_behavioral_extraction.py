# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 15:08:20 2023

@author: Guido Meijer
"""

import os
from os.path import join
import numpy as np
import pandas as pd
from glob import glob
from logreader import create_bp_structure, compute_onsets, compute_offsets

DATA_FOLDER = 'U:\\guido\\Subjects'

# Search for spikesort_me.flag
print('Looking for extract_me.flag..')
for root, directory, files in os.walk(DATA_FOLDER):
    if 'extract_me.flag' in files:
        print(f'\nFound extract_me.flag in {root}')
        
        data_file = glob(join(root, 'raw_behavior_data', '*.b64'))
        if len(data_file) == 0:
            print(f'No behavioral data found in {join(root, "raw_behavior_data")}')
            continue
        if len(data_file) > 1:
            print(f'Multiple behavioral log files found in {join(root, "raw_behavior_data")}')
            continue
                
        # Unpack log file
        data = create_bp_structure(data_file[0])
        
        # Get timestamps in seconds relative to first timestamp
        time_s = (data['startTS'] - data['startTS'][0]) / 1000000
        
        # Extract trial onsets
        if compute_onsets(data['digitalIn'][:, 8])[0] < compute_onsets(data['digitalIn'][:, 12])[0]:
            # Missed the first environment TTL so first trial starts at 0 s
            env_start = np.concatenate(([0], time_s[compute_offsets(data['digitalIn'][:, 12])]))
        else:
            env_start = time_s[compute_offsets(data['digitalIn'][:, 12])]

        # Extract reward times
        reward_times = time_s[compute_onsets(data['digitalOut'][:, 0])]
        
        # Extract all event timings
        all_env_end = time_s[compute_onsets(data['digitalIn'][:, 12])]
        all_first_obj_appear = time_s[compute_onsets(data['digitalIn'][:, 13])]
        all_obj1_enter = time_s[compute_onsets(data['digitalIn'][:, 8])]
        all_obj2_enter = time_s[compute_onsets(data['digitalIn'][:, 9])]
        all_obj3_enter = time_s[compute_onsets(data['digitalIn'][:, 10])]
        all_obj1_exit = time_s[compute_offsets(data['digitalIn'][:, 8])]
        all_obj2_exit = time_s[compute_offsets(data['digitalIn'][:, 9])]
        all_obj3_exit = time_s[compute_offsets(data['digitalIn'][:, 10])]
        all_sound1_onsets = time_s[compute_onsets(data['digitalIn'][:, 5])]
        all_sound2_onsets = time_s[compute_onsets(data['digitalIn'][:, 6])]
        all_sound3_onsets = time_s[compute_onsets(data['digitalIn'][:, 7])]
        all_sound1_offsets = time_s[compute_onsets(data['digitalIn'][:, 5])]
        all_sound2_offsets = time_s[compute_onsets(data['digitalIn'][:, 6])]
        all_sound3_offsets = time_s[compute_onsets(data['digitalIn'][:, 7])]
        
        # Only keep environment entries which are followed by the appearance of the first object
        discard_env_start = np.zeros(env_start.shape[0])
        for i, ts in enumerate(env_start[:-1]):
            if len(all_first_obj_appear[(all_first_obj_appear > ts)
                                        & (all_first_obj_appear < env_start[i+1])]) == 0:
                discard_env_start[i] = 1
        env_start = env_start[~(discard_env_start).astype(bool)]
        
        # Pre-allocate trial arrays
        env_end = np.empty(env_start.shape[0]-1)
        first_obj_appear = np.empty(env_start.shape[0]-1)
        obj1_enter = np.empty(env_start.shape[0]-1)
        obj2_enter = np.empty(env_start.shape[0]-1)
        obj3_enter = np.empty(env_start.shape[0]-1)
        obj1_exit = np.empty(env_start.shape[0]-1)
        obj2_exit = np.empty(env_start.shape[0]-1)
        obj3_exit = np.empty(env_start.shape[0]-1)
        obj1_rewards = np.empty(env_start.shape[0]-1).astype(int)
        obj2_rewards = np.empty(env_start.shape[0]-1).astype(int)
        obj3_rewards = np.empty(env_start.shape[0]-1).astype(int)
        obj1_position = np.empty(env_start.shape[0]-1).astype(int)
        obj2_position = np.empty(env_start.shape[0]-1).astype(int)
        obj3_position = np.empty(env_start.shape[0]-1).astype(int)
        sound_onset = np.empty(env_start.shape[0]-1)
        sound_offset = np.empty(env_start.shape[0]-1)
        sound_id = np.empty(env_start.shape[0]-1).astype(int)
        
        # Loop over trials and get events per trial
        for i, ts in enumerate(env_start[:-1]):
                        
            # Object enter and exit events
            these_obj1_enter = all_obj1_enter[(all_obj1_enter > ts) & (all_obj1_enter < env_start[i+1])]
            if len(these_obj1_enter) > 0:
                obj1_enter[i] = all_obj1_enter[(all_obj1_enter > ts) & (all_obj1_enter < env_start[i+1])][0]
            else:
                obj1_enter[i] = np.nan
            these_obj2_enter = all_obj2_enter[(all_obj2_enter > ts) & (all_obj2_enter < env_start[i+1])]
            if len(these_obj1_enter) > 0:
                obj2_enter[i] = all_obj2_enter[(all_obj2_enter > ts) & (all_obj2_enter < env_start[i+1])][0]
            else:
                obj2_enter[i] = np.nan
            these_obj3_enter = all_obj3_enter[(all_obj3_enter > ts) & (all_obj3_enter < env_start[i+1])]
            if len(these_obj3_enter) > 0:
                obj3_enter[i] = all_obj3_enter[(all_obj3_enter > ts) & (all_obj3_enter < env_start[i+1])][0]
            else:
                obj3_enter[i] = np.nan
            these_obj1_exit = all_obj1_exit[(all_obj1_exit > ts) & (all_obj1_exit < env_start[i+1])]
            if len(these_obj1_exit) > 0:
                obj1_exit[i] = all_obj1_exit[(all_obj1_exit > ts) & (all_obj1_exit < env_start[i+1])][0]
            else:
                obj1_exit[i] = np.nan
            these_obj2_exit = all_obj2_exit[(all_obj2_exit > ts) & (all_obj2_exit < env_start[i+1])]
            if len(these_obj1_exit) > 0:
                obj2_exit[i] = all_obj2_exit[(all_obj2_exit > ts) & (all_obj2_exit < env_start[i+1])][0]
            else:
                obj2_exit[i] = np.nan
            these_obj3_exit = all_obj3_exit[(all_obj3_exit > ts) & (all_obj3_exit < env_start[i+1])]
            if len(these_obj3_exit) > 0:
                obj3_exit[i] = all_obj3_exit[(all_obj3_exit > ts) & (all_obj3_exit < env_start[i+1])][0]
            else:
                obj3_exit[i] = np.nan
            
            # Number of rewards given per object
            obj1_rewards[i] = np.sum((reward_times >= obj1_enter[i]-0.1) & (reward_times < obj1_exit[i]))
            obj2_rewards[i] = np.sum((reward_times >= obj2_enter[i]-0.1) & (reward_times < obj2_exit[i]))
            obj3_rewards[i] = np.sum((reward_times >= obj3_enter[i]-0.1) & (reward_times < obj3_exit[i]))
               
            # Which position was the object in 
            obj1_position[i] = np.argsort([obj1_enter[i], obj2_enter[i], obj3_enter[i]])[0] + 1
            obj2_position[i] = np.argsort([obj1_enter[i], obj2_enter[i], obj3_enter[i]])[1] + 1
            obj3_position[i] = np.argsort([obj1_enter[i], obj2_enter[i], obj3_enter[i]])[2] + 1
            
            # Timestamp of appearance of object in first position
            first_obj_appear[i] = all_first_obj_appear[(all_first_obj_appear > ts) & (all_first_obj_appear < env_start[i+1])][0]
            
            # Sound on and offsets
            if all_sound1_onsets[(all_sound1_onsets > ts) & (all_sound1_onsets < env_start[i+1])].shape[0] > 0:
                sound_id[i] = 1
                sound_onset[i] = all_sound1_onsets[(all_sound1_onsets > ts) & (all_sound1_onsets < env_start[i+1])][0]
                sound_offset[i] = all_sound1_offsets[(all_sound1_offsets > ts) & (all_sound1_offsets < env_start[i+1])][0]
            elif all_sound2_onsets[(all_sound2_onsets > ts) & (all_sound2_onsets < env_start[i+1])].shape[0] > 0: 
                sound_id[i] = 2
                sound_onset[i] = all_sound2_onsets[(all_sound2_onsets > ts) & (all_sound2_onsets < env_start[i+1])][0]
                sound_offset[i] = all_sound2_offsets[(all_sound2_offsets > ts) & (all_sound2_offsets < env_start[i+1])][0]
            elif all_sound3_onsets[(all_sound3_onsets > ts) & (all_sound3_onsets < env_start[i+1])].shape[0] > 0: 
                sound_id[i] = 3
                sound_onset[i] = all_sound3_onsets[(all_sound3_onsets > ts) & (all_sound3_onsets < env_start[i+1])][0]
                sound_offset[i] = all_sound3_offsets[(all_sound3_offsets > ts) & (all_sound3_offsets < env_start[i+1])][0]
            
            # End of environment
            env_end[i] = all_env_end[(all_env_end > ts) & (all_env_end < env_start[i+1])][0]
            
        # Get wheel distance
        wheel_distance = data['longVar'][:, 1]
        
        # Get camera timestamps
        camera_times = time_s[compute_onsets(data['digitalIn'][:, 11])]
        
        # Save extracted events as ONE files
        np.save(join(root, 'trials.enterObj1.npy'), obj1_enter)
        np.save(join(root, 'trials.enterObj2.npy'), obj2_enter)
        np.save(join(root, 'trials.enterObj3.npy'), obj3_enter)
        np.save(join(root, 'trials.exitObj1.npy'), obj1_exit)
        np.save(join(root, 'trials.exitObj2.npy'), obj2_exit)
        np.save(join(root, 'trials.exitObj3.npy'), obj3_exit)
        np.save(join(root, 'trials.rewardsObj1.npy'), obj1_rewards)
        np.save(join(root, 'trials.rewardsObj2.npy'), obj2_rewards)
        np.save(join(root, 'trials.rewardsObj3.npy'), obj3_rewards)
        np.save(join(root, 'trials.positionObj1.npy'), obj1_position)
        np.save(join(root, 'trials.positionObj2.npy'), obj2_position)
        np.save(join(root, 'trials.positionObj3.npy'), obj3_position)
        np.save(join(root, 'trials.soundOnset.npy'), sound_onset)
        np.save(join(root, 'trials.soundOffset.npy'), sound_offset)
        np.save(join(root, 'trials.soundId.npy'), sound_id)
        np.save(join(root, 'trials.enterEnvironment.npy'), env_start[:-1])
        np.save(join(root, 'trials.exitEnvironment.npy'), env_end)
        np.save(join(root, 'trials.firstObjectAppear.npy'), first_obj_appear)
        np.save(join(root, 'reward.times.npy'), reward_times)
        np.save(join(root, 'wheel.distance.npy'), wheel_distance)
        np.save(join(root, 'wheel.times.npy'), time_s)
        np.save(join(root, 'camera.times.npy'), camera_times)
        
        # Build trial dataframe and also save that
        trials = pd.DataFrame(data={
            'enterEnvironment': env_start[:-1], 'exitEnvironment': env_end,
            'soundOnset': sound_onset, 'soundOffset': sound_offset, 'soundId': sound_id,
            'firstObjectAppear': first_obj_appear,
            'enterObj1': obj1_enter, 'enterObj2': obj2_enter, 'enterObj3': obj3_enter,
            'exitObj1': obj1_exit, 'exitObj2': obj2_exit, 'exitObj3': obj3_exit,
            'rewardsObj1': obj1_rewards, 'rewardsObj2': obj2_rewards, 'rewardsObj3': obj3_rewards,
            'positionObj1': obj1_position, 'positionObj2': obj2_position, 'positionObj3': obj3_position
            })
        trials.to_csv(join(root, 'trials.csv'))
        
        # Delete extraction flag
        os.remove(join(root, 'extract_me.flag'))
        if np.sum(np.isnan(obj1_enter)) > 0:
            print(f'{np.sum(np.isnan(obj1_enter))} missing enterObj1 events')
        if np.sum(np.isnan(obj2_enter)) > 0:
            print(f'{np.sum(np.isnan(obj2_enter))} missing enterObj2 events')
        if np.sum(np.isnan(obj3_enter)) > 0:
            print(f'{np.sum(np.isnan(obj3_enter))} missing enterObj3 events')
        if np.sum(np.isnan(obj1_exit)) > 0:
            print(f'{np.sum(np.isnan(obj1_exit))} missing exitObj1 events')
        if np.sum(np.isnan(obj2_exit)) > 0:
            print(f'{np.sum(np.isnan(obj2_exit))} missing exitObj2 events')
        if np.sum(np.isnan(obj3_exit)) > 0:
            print(f'{np.sum(np.isnan(obj3_exit))} missing exitObj3 events')
        print(f'Successfully extracted session in {root}')
        
        