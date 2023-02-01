import sys
import glob
import os
import pandas as pd

sys.path.append('..')
from annotation.converters import saga_to_table


saga_dir = '/Users/roso8920/Dropbox (Emotive Computing)/LEVI/saga8'

srclist = glob.glob(os.path.join(saga_dir,'*.txt'), recursive=False)
for f in srclist:
    tbl=saga_to_table(f)
    tbl.to_csv(f.replace('.txt','.csv'), sep='|')
