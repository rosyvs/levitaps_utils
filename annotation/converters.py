import os
import csv
import re
import pandas as pd

# functions to convert between different transcript/annotation formats

# useful generic format is a table with
# [uttID, speaker, utterance, start_sec, end_sec]


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
                rows.append([speaker,transcript,start_sec,None])
                #print([speaker,transcript,timestamp])
            count+=1
    utt_table = pd.DataFrame(rows, columns=['speaker','transcript','start_sec','end_sec'])
    return(utt_table)

def HHMMSS_to_sec(time_str):
    """Get Seconds from timestamp string with milliseconds."""
    if time_str.count(':')==2:
        h, m, s = time_str.split(':')
    elif time_str.count(':')==3:
        print('Weird time format detected - HH:MM:SS:tenths - please verify this is how you want the time interpreted')
    # "human error" fix for files with : as Second/millisecond delimiter and tenths of a second only, some early transcripts (2021) used this format
        h, m, s, ms = time_str.split(':')
        s = int(s)+float(ms)/10
    elif time_str.count(':')==1:
        # print('missing HH from timestamp, assuming MM:SS')
        m, s = time_str.split(':')
        h=0
    else:
        print(f'input string format not supported: {time_str}')
    return int(h) * 3600 + int(m) * 60 + float(s) 