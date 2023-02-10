import os
import sys
sys.path.append('..')
from rosy_asr_utils import get_sess_audio, HHMMSS_to_sec
from pydub import AudioSegment
from pathlib import Path
import os
import csv
import glob
import shutil
from extractSamples import extractSamples
from prepSessDirs import prepSessDirs

extract_timings_csv = '../configs/LEVI/164_trim_timings.csv'

# --NEW TUTORS
# prepSessDirs.py configs/LEVI/src_new_tutors.txt /home/rosy/LEVI/media/original_164/new_tutors/ -l -s configs/LEVI/new_tutors.txt
datapath = '../../LEVI/media/original_164/new_tutors/'
outpath = '../../LEVI/media/trimmed_164/new_tutors/'

extractSamples(datadir=datapath,
                    extract_timings_csv=extract_timings_csv, 
                    outdir_stem=outpath, 
                    suffix='', 
                    convert=False,
                    convert_to_wav=False)

# copy trimmed files "loose" to OneDrive synced folder 
export_path = '../../OneDrive/Saga videos/original_164/trimmed_files/new_tutors/'
srclist = glob.glob(os.path.join(outpath,'**/*.mp4'), recursive=True)
for f in srclist:
    shutil.copy(f, export_path)


# --RETURNING TUTORS
datapath = '../../LEVI/media/original_164/returning_tutors/'
sesspath_list =prepSessDirs(
    files='../configs/LEVI/src_return_tutors.txt', 
    outdir=datapath, 
    link_media=True, 
    convert_to_wav=False,
    mode = 'media')
with open('../configs/LEVI/returning_tutors.txt','w') as f:
    for i in sesspath_list:
        f.write(i + '\n')

outpath = '../../LEVI/media/trimmed_164/returning_tutors/'

extractSamples(datadir=datapath,
                    extract_timings_csv=extract_timings_csv, 
                    outdir_stem=outpath, 
                    suffix='', 
                    convert=False,
                    convert_to_wav=False)

# copy trimmed files "loose" to OneDrive synced folder 
export_path = '../../OneDrive/Saga videos/original_164/trimmed_files/returning_tutors/'
srclist = glob.glob(os.path.join(outpath,'**/*.mp4'), recursive=True)
for f in srclist:
    shutil.copy(f, export_path)
