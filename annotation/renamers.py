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
    SID_to_FN={}
    FN_to_SID={}
    with open(path,encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert (headers[0]=='File_Name') & (headers[1]=='Session_ID'), "Headers are wrong, expected 'File_Name' and 'Session_ID'"

        for line in reader:
            filename,sessionID=line
            filename=filename.split('.')[0]
            if (len(filename.strip())>0 and len(sessionID.strip())>0): 
                SID_to_FN[sessionID]=filename
                FN_to_SID[filename]=sessionID
    return(SID_to_FN, FN_to_SID)


def rename_files_SID_to_FN(path, recursive=True, overwrite=False):
    SID_to_FN, _=make_SessionID_map()

    for sID in SID_to_FN.keys():
        srclist = glob.glob(os.path.join(path,'**', f'*{sID}.*'), recursive=True)
        # print(f'siD: {sID}')
        # print(srclist)
        for srcpath in srclist:
            newpath = srcpath.replace(sID, SID_to_FN[sID])
            print(newpath)    
            if overwrite==True:
                shutil.move(srcpath, newpath)
            else:
                shutil.copy(srcpath, newpath)



    # # get sessnames
    # sesslist = [s for s in os.listdir(path) ]
    # srclist = [os.path.join(src_dir, filename) for filename in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, filename))]
    # for src in srclist:
    #     sessname_matches = [sessname in src for sessname in sesslist]
    #     if sum(sessname_matches)>1:
    #         print('!!!!    multiple matches, will take longest match. TODO: implement this you dope')
    #     elif not any(sessname_matches):
    #         print(f'!!!!    no sessname matches for file {src}')
    #     else: 
    #         sessname = sesslist[sessname_matches.index(True)]
    #         print(f'...copying to {sessname}')
    #         shutil.copy(src, os.path.join(dest_dir,sessname))

def rename_files_FN_to_SID(path, recursive=True):
    _, FN_to_SID=make_SessionID_map()
