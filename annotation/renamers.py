import csv
import os
import glob
import shutil



# rename files from original filename (hexadecimal salad) to Session_ID (human readable) and back
global DEFAULT_MAP_PATH
DEFAULT_MAP_PATH = '../../SessionIDs_from_catalog.csv'

def make_SessionID_map(path=DEFAULT_MAP_PATH):
    """generate dictionary from csv file with columns for filename and session ID - 
    copied from columsn 1 & 2 of the Catalog on OneDrive
    """
    with open(path,encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert headers[0]=='File_Name' & headers[1]=='Session_ID', "Headers are wrong, expected 'File_Name' and 'Session_ID'"
    SID_to_FN={}
    FN_to_SID={}
    for line in reader:
        #print value in MyCol1 for each row
        filename,sessionID=line
        SID_to_FN[filename]=sessionID
        FN_to_SID[sessionID]=filename
    return(SID_to_FN, FN_to_SID)


def SessionID_to_FileName(path, recursive=True):
    SID_to_FN, _=make_SessionID_map()

def FileName_to_SessionID(path, recursive=True):
    _, FN_to_SID=make_SessionID_map()
