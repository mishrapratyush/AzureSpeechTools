"""
The ``stt-preprocess.tools.text`` module provides functions to do common text preprocessing steps
"""

import re
from itertools import groupby
import os
import json
import shutil
import sys
from pathlib import Path

def remove_punctuation(input_str):
    """
    Removes punctuations from input string
    :param input_str: String to be processed.
    :return: string with all punctuations returned
    """
    lines = input_str.split('\n')
    output_lines = []
    for line in lines:
        temp_line = re.sub(r'[^a-zA-Z0-9\s\'\-\,]', '', line)
        temp_line = re.sub(' +', ' ', temp_line)
        temp_line = temp_line.strip()
        output_lines.append(temp_line)
    
    output_lines = list(filter(lambda line: line != '', output_lines))
    return '\n'.join(output_lines)


def find_repetition(input_str):
    """
    Removes repetitions from string. Optionally specify minimum number
    of repetitions to keep before removing the rest
    :param input_str: String to be processed.
    :return: string with repetitions removed
    """
    lines = input_str.split('\n')
    duplicates = []
    for line_index,line in enumerate(lines):
        split_line = line.split(' ')
        
        # one-word repetition
        for index in range(len(split_line) - 1):
            curr = split_line[index]
            next_line = split_line[index+1]
            if curr == next_line:
                duplicates.append((line_index, curr))

        # two-word repetition
        index = 0
        while index < len(split_line) - 3:
            curr = split_line[index] + " " + split_line[index+1]
            next_line = split_line[index+2] + " " + split_line[index+3]
            if curr == next_line:
                duplicates.append((line_index, curr))
                index += 2
                continue
            else:
                index += 1

        # three-word repetition
        index = 0
        while index < len(split_line) - 5:
            curr = split_line[index] + " " + split_line[index+1] + " " + split_line[index+2]
            next_line = split_line[index+3] + " " + split_line[index+4] + " " + split_line[index+5]
            if curr == next_line:
                duplicates.append((line_index, curr))
                index += 3
            else:
                index += 1
    
    duplicates = list(set(duplicates))
    duplicates.sort(key = lambda x: x[0]) 
    return input_str, duplicates


def spell_out_numbers(inputs_str):
    """
    Converts any string containing numerals to equivalent words representations
    :param input_str: String to be processed.
    :return: string numerals converted to words.
    """
    pass

def replace_hypen(inputs_str):
    return inputs_str.replace("--"," ").replace("-"," ")

def filter_phrases(input_str, filter_list):
    """
    Filters out phrases/words from the input string
    :param input_str: String to be processed.
    :return: string with phrases from filter_list removed.
    """
    for phrase in filter_list:
        input_str = input_str.replace(phrase,'')
    return input_str

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--TranscriptFldrPath", help="Path to folder containing transcripts")
    parser.add_argument("--ConfigFilePath", help="Path to config file for text normalization")
    parser.add_argument("-m", "--merge", help="merge outputs files",
                action="store_true")
    args = parser.parse_args()

    config_file = open(args.ConfigFilePath, 'r')
    config = json.load(config_file)
    config_file.close()

    if 'textNormalization' not in config:
        raise ValueError("Please specify text normalization configurations in file")

    text_normalization_config = config['textNormalization']

    output_path = Path(args.TranscriptFldrPath)
    output_path =os.path.join(output_path.parent.absolute(), 'TranscriptNormalized')

    if not os.path.exists(output_path): # make path if not exists
        os.makedirs(output_path)
    else:
        for f in os.listdir(output_path): # delete all files in path
            os.remove(os.path.join(output_path, f))

    files = os.listdir(args.TranscriptFldrPath)
    if len(files) == 0:
        print("Input directory has no files, no output was generated")
        exit(1)

    for input_file_name in files:
        try:
            input_file_path = os.path.join(args.TranscriptFldrPath,input_file_name)
            input_file = open(input_file_path, 'r')
            processed_string = input_file.read()

            if text_normalization_config.get('removePunctuation') == True:
                processed_string = remove_punctuation(processed_string)
            
            if 'filterPhrases' in text_normalization_config:
                processed_string = filter_phrases(processed_string, text_normalization_config['filterPhrases']['phraseList'])
            
            if 'findRepetition' in text_normalization_config:
                processed_string, duplicates = find_repetition(processed_string)
                print("Duplicates:\nFile Name\tLine No.\tDuplicate Text")
                for duplicate in duplicates:
                    print(f"{input_file_name}\t{duplicate[0]}\t{duplicate[1]}")
            
            if text_normalization_config.get('toLowerCase') == True:
                processed_string = processed_string.lower()

            if text_normalization_config.get('replaceHypens') == True:
                processed_string = replace_hypen(processed_string)
            
            if text_normalization_config.get('outputSingleLine') == True:
                processed_string = processed_string.replace("\n", ' ')


            output_file_path = os.path.join(output_path, input_file_name.split('.')[0] + '_normalized.txt')
            output_file = open(output_file_path, 'w', encoding="utf-8")
            output_file.write(processed_string)
            output_file.close()
        
        except:
            print(f"Unable to extract file: {input_file} \n Error:{sys.exc_info()[0]}")

    if args.merge:
        # create merged file
        merge_output_path = os.path.join(output_path, 'transcript_normalized.txt')
        part_files = os.listdir(output_path)

        # merge all part files
        with open(merge_output_path, 'wb') as outfile:
            for filename in part_files:
                with open(os.path.join(output_path,filename), 'rb') as readfile:
                    shutil.copyfileobj(readfile, outfile)
        
        # clean up part files
        for f in part_files:
            os.remove(os.path.join(output_path, f))

    print(f"Normalized transcripts written to: {output_path} \nUsing config file:{args.ConfigFilePath}")