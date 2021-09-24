"""
The ``stt-preprocess.tools.webvtt`` module provides functions to extract text content from WebVTT Files:
"""

import webvtt
import os
import tempfile
import re
import sys
import shutil
from pathlib import Path


def extract_text_raw(webvtt_input_str):
    """
    Extracts transcripts from WebVTT tiles
    :param input_str: string containing contents of a valid WebVTT file.
    :return: string with just transcripts text
    """
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(webvtt_input_str.encode())
    temp.close()

    transcript = ''
    for caption in webvtt.read(temp.name):
        transcript = transcript + ' '.join(caption.text.strip().splitlines()) + ' '
    os.unlink(temp.name)
    assert not os.path.exists(temp.name)
    
    return transcript

def extract_text(webvtt_input_str):
    """
    Extracts transcripts from WebVTT tiles and does preprocessing
    :param input_str: string containing contents of a valid WebVTT file.
    :return: string with just transcripts text
    """
    raw_text = extract_text_raw(webvtt_input_str)
    transcript = raw_text.replace('\n','')
    res = re.split(r'\.|\?', transcript)
    return "\n".join([segment.strip() for segment in res])


def generate_webvtt(transcript_input_str, word_level_timestamps):
    """
    Generates subtitles in WebVTT format from text and word level timestamps.
    :param input_str: plain text transcription
    :param word_level_timestamps: associated word_level_timestamps generated from Speech-To-Text process.
    :return: string in valid WebVTT format.
    """
    pass


# when invoked directly

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", help="Defines the operation to be performed (extract/generate)", type=str, default='extract', choices=['extract','generate'])
    parser.add_argument("--WebVttFldrPath", help="Path to folder containing the WebVTT Files")
    parser.add_argument("-m", "--merge", help="merge outputs files",
                    action="store_true")
    args = parser.parse_args()

    if args.operation == 'extract':

        output_path = Path(args.WebVttFldrPath)
        output_path =os.path.join(output_path.parent.absolute(), 'TranscriptExtract')

        if not os.path.exists(output_path): # create path if not exists
            os.makedirs(output_path)
        else:
            for f in os.listdir(output_path): # delete all files in path
                os.remove(os.path.join(output_path, f))
        
        files = os.listdir(args.WebVttFldrPath)

        if len(files) == 0:
            print("Input directory has no files, no output was generated")
            exit(1)

        for input_file in files:
            with open(os.path.join(args.WebVttFldrPath, input_file), encoding='utf-8-sig') as f:
                try:
                    f_string = f.read()
                    transcript = extract_text(f_string)
                    output_file_path = os.path.join(output_path, input_file.split('.')[0] + '_extract.txt')
                    output_file = open(output_file_path, 'w', encoding="utf-8")
                    output_file.write(transcript)
                    output_file.close()
                except webvtt.errors.MalformedFileError:
                    print(f"Unable to extract file: {input_file} \n The input file is malformed, please make sure the file is valid.")
                except:
                    print(f"Unable to extract file: {input_file} \n Error:{sys.exc_info()[0]}")
        
        if args.merge:
            # create merged file
            merge_output_path = os.path.join(output_path, 'extract_output.txt')
            part_files = os.listdir(output_path)

            # merge all part files
            with open(merge_output_path, 'wb') as outfile:
                for filename in part_files:
                    with open(os.path.join(output_path,filename), 'rb') as readfile:
                        shutil.copyfileobj(readfile, outfile)
            
            # clean up part files
            for f in part_files:
                os.remove(os.path.join(output_path, f))
        
        print(f"Extracted transcripts written to: {output_path}")

    else:
        print("Generation not currently supported")
