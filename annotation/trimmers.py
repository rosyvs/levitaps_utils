from pathlib import Path
import os
import csv
import subprocess
import pandas as pd
import sys
sys.path.append('..')

from annotation.converters import HHMMSS_to_sec

def trim_media(media_in,
                media_out,
                start,
                end): 
    
    # options for writing out audio if converting
    WAV_CHANNELS = 1
    WAV_SAMPLE_RATE = 16000
    
    media_type = Path(media_in).suffix
    ext = Path(media_out).suffix

    if isinstance(start, str):
        start_sec = HHMMSS_to_sec(start)
    else: 
        start_sec = float(start)
    if isinstance(end, str):
        end_sec = HHMMSS_to_sec(end)
    else:
        end_sec = float(end)

    if ext == '.wav':
    # convert to wav with standard format for audio models
        print(f'...Using ffmpeg to trim video from {start} to {end} \n   and convert to {WAV_SAMPLE_RATE}Hz WAV with {WAV_CHANNELS} channels...')            
        print(f'...generating {media_out}...')            

        subprocess.call(['ffmpeg',
        '-y',
        '-i',
        media_in,
        '-ss',
        f'{start_sec}',
        '-to',
        f'{end_sec}',
        '-acodec',
        'pcm_s16le',
        '-ac',
        WAV_CHANNELS,
        '-ar',
        WAV_SAMPLE_RATE,
        media_out,
        '-hide_banner', 
        '-loglevel', 
        'warning'        
        ],shell=False)   
    
    else: 

        print(f'...Using ffmpeg to trim video from {start_sec} to {end_sec}...')      
        print(f'...generating {media_out}...')            
      
        subprocess.call(['ffmpeg',
        '-y',
        '-i',
        media_in,
        '-ss',
        f'{start_sec}',
        '-to',
        f'{end_sec}',
        '-c',
        'copy',
        media_out,
        '-hide_banner', 
        '-loglevel', 
        'warning'        
        ],shell=False)             

def trim_media_batch(extract_timings_csv,
                    outpath, 
                    suffix='', 
                    convert_to=False):
    """trim a batch of media files given a csv of timings

    Args:
        extract_timings_csv (str): path to csv with columns:
            filepath, start (HH:MM:SS), end (HH:MM:SS) 
        outpath (str): output path 
        suffix (str, optional): save output trimmed files with this suffix. Defaults to ''.
        convert_to (bool, optional): [None, 'wav','mp4']. Defaults to False. 
    Returns:
        outfiles (list): list of file paths created        
    """                    

    

    os.makedirs(outpath, exist_ok=True)

    samples_df = pd.read_csv(
        extract_timings_csv,
        skip_blank_lines=True, 
        index_col=False,
        names=['media_in','startHMS','endHMS'], 
        header=0
        ).dropna().sort_values(
            by='media_in',ignore_index=True).reset_index(drop=True)

    print(f'TRIMMING {len(samples_df.index)} FILES...')

    # enumerate samples by session and check if there are multiple samples from a given session
    samples_df['count'] = samples_df.groupby('media_in').cumcount()
    if not os.path.exists(outpath):
            os.makedirs(outpath)

    outfiles=[]
    for i, rec in samples_df.iterrows():
        media_in,startHMS,endHMS, count = rec.values
        suffix_use = f'{suffix}{count}' if count > 0 else suffix # if multiple samples per recording, give a diffrent name          

        if not os.path.exists(media_in):
            print(f'!!!WARNING: media not found: {media_in}')
            continue

        media_type = Path(media_in).suffix
        sessname = Path(media_in).stem
        print(f'...Input media: {media_in}')

        if convert_to=='wav':
            ext = '.wav'
        elif convert_to=='mp4':
            ext = '.mp4'
        else: 
            ext = media_type
        
        outfile = os.path.expanduser(os.path.join(outpath,f'{sessname}{suffix_use}{ext}'))

        trim_media(media_in, outfile, HHMMSS_to_sec(startHMS), HHMMSS_to_sec(endHMS))

        outfiles.append(outfile)
    return(outfiles)