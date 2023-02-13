import os
import csv
import re
import pandas as pd

# functions to convert between different transcript/annotation formats

# useful generic format is a table with
# [uttID, speaker, transcript, start_sec, end_sec]

# separate function to write to csv, tsv or ELAN compatible (ELAN interprets ALL commas as delimiter)

def HHMMSS_to_sec(time_str):
    """Get Seconds from timestamp string with milliseconds."""
    if not time_str:
        return None
    if time_str.count(':')==2:
        h, m, s = time_str.split(':')
    elif time_str.count(':')==3:
    # weird timestamps where there is a field followign seconds delimited by colon
        h, m, s, u = time_str.split(':')
        # determine whether ms field is in tenths or hundredths or thousandths by countng how many digits
        if len(u)==1:
            print('Weird time format detected - HH:MM:SS:tenths - please verify this is how you want the time interpreted')
            ms = float(u)/10
        elif len(u)==2: # hundredths
            ms = float(u)/100
        elif len(u)==3: # hundredths
            ms = float(u)/1000
        else:
            print(f'input string format not supported: {time_str}')
            return None
        s = int(s)+ms
    elif time_str.count(':')==1:
        # print('missing HH from timestamp, assuming MM:SS')
        m, s = time_str.split(':')
        h=0
    else:
        print(f'input string format not supported: {time_str}')
        return None
    return int(h) * 3600 + int(m) * 60 + float(s) 

def docx_scraped_tsv_to_table(ooona_file):
    # ooona output is a table in a word docx, 
    # for now manually copying this out and saving as tsv
    # but the timestamp format is wrong
    # input cols are SHOT	START	END	SPEAKER	DIALOGUE

    with open(ooona_file) as in_file:
        reader = csv.reader(in_file, delimiter="\t")
        next(reader) # skip header
        rows=[]
        for i,line in enumerate(reader):
            utt_ix, start_time, end_time, speaker, transcript = line
            start_sec = HHMMSS_to_sec(start_time)
            end_sec = HHMMSS_to_sec(end_time)
            rows.append([utt_ix,speaker,transcript,start_sec,end_sec])
    utt_table = pd.DataFrame(rows, columns=['uttID','speaker','transcript','start_sec','end_sec'])
    return(utt_table)
    # table = pd.read_csv(ooona_file, sep='\t')

def molly_xlsx_to_table(xl_file):
    # contractor transcribers provide an xlsx with the following columns
    # utt_ix:	int
    # Timecode: "HH:MM:SS:ss - HH:MM:SS:ss"	
    # Duration:	HH:MM:SS:ss 
    # Speaker:	str
    # Dialogue:	str 
    # Annotations:	blank
    # Error Type: blank
    with pd.ExcelFile(xl_file) as xls:
        sheetname = xls.sheet_names
        table = pd.DataFrame(pd.read_excel(xls, sheetname[0]))
    table[['start_time','end_time']] = table['Timecode'].str.split('-',expand=True)
    table['start_sec'] = table['start_time'].str.strip().apply(HHMMSS_to_sec)
    table['end_sec'] = table['end_time'].str.strip().apply(HHMMSS_to_sec)
    table.drop(labels=['Annotations','Error Type','Duration'], axis=1, inplace=True)
    table=table[['#','Speaker','Dialogue','start_sec','end_sec']]
    table.rename(columns={'#':'uttID','Speaker':'speaker', 'Dialogue':'transcript'}, inplace=True)

    return table

def saga_to_table(saga_txt):
    # saga's own transcripts are txt given in the following format
    # 
    # speaker (start time MM:SS)
    # utterance
    # <blank line>
    # TODO: make more robust by pattern matching instead of modulo
    with open(saga_txt) as in_file:
        reader = csv.reader(in_file, delimiter="\n")
        count = 0
        rows=[]
        for i,line in enumerate(reader):
            print((count,line))
            if count%3 == 0:
            # utt = utt.split('\n')  # now speaker (time) , transcript
                # transcript = utt[1]
                spk_time = line[0].split('(')
                if len(spk_time)<2:
                    # print('!!!speaker not changed')
                    # print(line)
                    timestamp = spk_time[0].strip('):( ')
                    speaker=rows[-1][0]   # prev speaker        

                else:
                    speaker = spk_time[0]    
                    timestamp = spk_time[1].replace('):','')             
                    # print(timestamp)
                start_sec = HHMMSS_to_sec(timestamp)

            if count%3 == 1:
                transcript = line[0]
            if count%3 == 2:
                rows.append([i,speaker,transcript,start_sec,None])
                #print([speaker,transcript,timestamp])
            count+=1
    utt_table = pd.DataFrame(rows, columns=['uttID','speaker','transcript','start_sec','end_sec'])
    return(utt_table)

def table_to_ELAN_tsv(table:pd.DataFrame, path:str):
    # write table to tsv compatible with ELAN import
    table.to_csv(path, sep='\t')

def table_to_standard_csv(table:pd.DataFrame, path:str):
    # write table to standard csv format agreed upon by whole team

    # TODO: convert times in seconds back to HH:MM:SS? 
    # TODO: split utterances into sentences? 
    table.to_csv(path,index=False, float_format='%.3f')

def table_to_utt_labels_csv(table:pd.DataFrame, path:str):
    # write table to utt_labels csv format comaptable w rosy's isatasr lib
    table.drop('uttID', axis=1, inplace=True)
    table.rename(columns={'transcript':'utterance'}, inplace=True)
    table.to_csv(path,index=False, float_format='%.3f')
    
