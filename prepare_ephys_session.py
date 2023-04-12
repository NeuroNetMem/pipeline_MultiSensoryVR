# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 13:44:12 2023 by Guido Meijer
"""

import argparse
import datetime
from os.path import join


def main(mouse):
    SUBJECT_NAME = mouse
    DATA_FOLDER = 'K:\\NeuropixelData'

    DATE = datetime.datetime.now().date().isoformat()

    SESSION_FOLDER = join(DATA_FOLDER, SUBJECT_NAME, DATE, "raw_ephys_data")
    SESSION_FOLDER.mkdir(parents=True, exist_ok=True)
    print(f"Created {SESSION_FOLDER}")
    
    with open(join(SESSION_FOLDER, 'spikesort_me.flag'), 'w'):
        pass
    print('Created spikesort_me.flag')
   
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare ephys PC for ephys recording session")
    parser.add_argument("mouse", help="Mouse name")
    args = parser.parse_args()

    main(args.mouse)
