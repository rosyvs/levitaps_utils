
import sys
sys.path.append('..')
import itertools
import csv
import pandas as pd
import os
from pathlib import Path
from annotation.trimmers import trim_media_batch, trim_media
from annotation.converters import HHMMSS_to_sec, molly_xlsx_to_table, table_to_ELAN_tsv
from annotation.renamers import rename_files_FN_to_SID, rename_files_SID_to_FN, make_SessionID_map

# TODO call the renameers functions to convert FileNames and SessionID to match between media and transcript
SID_to_FN, FN_to_SID=make_SessionID_map()

extract_timings_csv='/Users/roso8920/Dropbox (Emotive Computing)/LEVI/5min_HiFi/sample_timings.csv'

# TODO: replace with shared source dir here  /Users/roso8920/Library/CloudStorage/OneDrive-SharedLibraries-UCB-O365/Jennifer K Jacobs - CSVs
# transcript_xlsx_path = '/Users/roso8920/Dropbox (Emotive Computing)/LEVI/human_transcripts/molly_transcripts/xlsx'
transcript_xlsx_path = '/Users/roso8920/Library/CloudStorage/OneDrive-SharedLibraries-UCB-O365/Jennifer K Jacobs - Transcribed'
out_dir = '/Users/roso8920/Library/CloudStorage/OneDrive-UCB-O365/LEVI/5min_HiFi/media/'
tsv_out_dir = '/Users/roso8920/Library/CloudStorage/OneDrive-UCB-O365/LEVI/5min_HiFi/ELAN-ready-transcripts/'

convert_to=False
sample_len_s = 300
suffix='_5min'

# ### option 1: assume correct paths are alrady given in extract_timings_csv:
# trim_media_batch(extract_timings_csv,
#                     out_dir, 
#                     suffix='_5min', 
#                     convert_to=convert_to)

# ### option 2: 
# assume extract_timings_csv just has file identifier (Session_ID or FileName) and start time
# as this is what can be copied from the Data Catalog
# we will add the appropriate path, end time, and convert between Session_ID and FileName as needed

# location of session directories where full length files reside
sess_root_dir = '/Users/roso8920/Library/CloudStorage/OneDrive-UCB-O365/LEVI/media/'

with open(extract_timings_csv,'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row)==2:
            media_in, start = row
            start_sec=HHMMSS_to_sec(start)
            end_sec = start_sec+ sample_len_s
        elif len(row)==3:
            media_in, start, end = row
            start_sec=HHMMSS_to_sec(start)
            end_sec=HHMMSS_to_sec(end)
        media_type = Path(media_in).suffix
        media_name = Path(media_in).stem
        
        # converts to SID if poss otherwise just keep media name
        SID=FN_to_SID.get(media_name,media_name)
        print(f'Session_ID: {SID}')
        media_path = os.path.expanduser(os.path.join(sess_root_dir,f'{media_name}{media_type}'))
        print(f'...Input media path: {media_path}')

        if convert_to=='wav':
            ext = '.wav'
        elif convert_to=='mp4':
            ext = '.mp4'
        else: 
            ext = media_type
        
        outfile = os.path.expanduser(os.path.join(out_dir,f'{SID}{suffix}{ext}'))

        trim_media(media_path, outfile, start_sec, end_sec)

        # trim ELAN files 
        # these might be named with the Session_ID instead of FileName matching the media
        xlsx_path = os.path.expanduser(os.path.join(transcript_xlsx_path,f'{media_name}.xlsx'))
        if not os.path.exists(xlsx_path): # maybe because xlsx used the other naming convention
            if media_name in FN_to_SID.keys():
                media_name2=FN_to_SID[media_name]
            elif media_name in SID_to_FN.keys():
                media_name2=SID_to_FN[media_name]
            else:
                print(f'!!! xlsx transcript not found for {media_name} in {transcript_xlsx_path} using either naming convention')
                continue
            xlsx_path = os.path.expanduser(os.path.join(transcript_xlsx_path,f'{media_name2}.xlsx'))
            if not os.path.exists(xlsx_path): 
                print(f'!!! xlsx transcript not found for {media_name} in {transcript_xlsx_path} using either naming convention')
                continue
        
        tbl = molly_xlsx_to_table(xlsx_path)
        tsv_out_file = os.path.expanduser(os.path.join(tsv_out_dir, f'{SID}{suffix}.tsv'))
        # trim table
        tbl2=tbl
        tbl2['start_sec'] = tbl['start_sec'] - start_sec
        tbl2['end_sec']= tbl['end_sec'] - start_sec

        tbl2=tbl2.loc[tbl2['start_sec']>0,]
        tbl2=tbl2.loc[tbl2['end_sec']<sample_len_s,]
        table_to_ELAN_tsv(tbl2, tsv_out_file)
        