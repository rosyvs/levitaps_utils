import sys
import glob
import os
import pandas as pd
from pathlib import Path

sys.path.append('..')
from annotation.converters import molly_xlsx_to_table, table_to_utt_labels_csv
from annotation.renamers import rename_files_SID_to_FN, make_SessionID_map

src_dir = '/Users/roso8920/Dropbox (Emotive Computing)/LEVI/human_transcripts/molly_transcripts/xlsx'
srclist = glob.glob(os.path.join(src_dir,'*.xlsx'), recursive=False)

SID_to_FN, FN_to_SID=make_SessionID_map()

srclist = rename_files_SID_to_FN(src_dir)

dest_dir = '/Users/roso8920/Dropbox (Emotive Computing)/LEVI/human_transcripts/molly_transcripts/utt_labels/'
os.makedirs(dest_dir, exist_ok=True)
for f in srclist:
    sessname = Path(f).stem.strip('.') # some have extra . at end of filename
    tbl = molly_xlsx_to_table(f)
    csvf = os.path.join(dest_dir, f'utt_labels_{sessname}.csv')
    table_to_utt_labels_csv(tbl,csvf)