import os
from os.path import join
import pandas as pd
from glob import glob
import numpy as np
import deeplabcut
import subprocess

DATA_FOLDER = '/mnt/imaging1/guido/Subjects'
CONFIG_FILE = '/mnt/data/guido/DLC/find-eye-Guido-2023-08-23/config.yaml'
EYE_WIDTH_PX = 80
EYE_HEIGHT_PX = 70

for root, directory, files in os.walk(DATA_FOLDER):
    if 'eyetrack_me.flag' in files:
        print(f'\nFound eyetrack_me.flag in {root}')
        
        
        video_file = glob(join(root, 'raw_video_data', '*.h264'))
        if len(video_file) != 1:
            print(f'No video found in {join(root, "raw_video_data")}')
            continue
        if len(video_file) > 1:
            print(f'Multiple videos found in {join(root, "raw_video_data")}')
            continue

        # Convert to mp4
        subprocess.call(['ffmpeg', '-i', video_file[0], '-codec' 'copy', video_file[0][:-5] + '.mp4'])
        os.remove(video_file[0])  # delete .h264 video file 
        new_video = video_file[0][:-5] + '.mp4'
        
        # Extract a single frame from the video
        subprocess.call('ffmpeg', '-ss', '00:10:00', '-i', new_video, '-frames:v', '1', '-q:v', '2', join(root, 'raw_video_data', 'single_frame.jpg'))
        
        # Run DLC on single frame to determine the position of the eye
        deeplabcut.analyze_time_lapse_frames(CONFIG_FILE, join(root, 'raw_video_data'), frametype='.jpg',shuffle=1, trainingsetindex=0, gputouse=None, save_as_csv=True, rgb=True)

        # Get position of the eye
        dlc_file = glob(join(root, 'raw_video_data', '*.csv'))
        dlc_output = pd.read_csv(dlc_file[0])
        eye_x = int(float(dlc_output.iloc[2, 1]))
        eye_y = int(float(dlc_output.iloc[2, 2]))

        # Crop out the eye into new video
        subprocess.call(['ffmpeg', '-i', {new_video}, '-filter:v', f'crop={EYE_WIDTH_PX}:{EYE_HEIGHT_PX}:{int(eye_x-EYE_WIDTH_PX/2)}:{int(eye_y-EYE_HEIGHT_PX/2)}', '-y', join(root, 'raw_video_data', 'eye_crop.mp4')])

        # Apply curve to increase low to mid level brightness
        subprocess.call(['ffmpeg', '-i', join(root, 'raw_video_data', 'eye_crop.mp4'), '-vf', "curves=all='0/0 0.2/0.6 1/1',format=yuv420p", '-c:a', 'copy', '-y', join(root, 'raw_video_data', 'eye_crop_adjusted.mp4')])

        