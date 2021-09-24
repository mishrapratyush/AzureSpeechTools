# Overview
Scripts here are to help you with extracting dataset from specific file types and also do preprocessing of text files. They include common preprocessing steps required to prepare training data.

Contains two main scripts:
1. WebVTT Tools
2. Text Tools

## WebVTT Tools
This tool allows you to extract plain text from WebVTT Subtitles files.

To use this tool run:

```shell
python webvtt_tools.py -m --WebVttFldrPath <PATH TO WEBVTT FILES>
```

Notes:
1. The optional -m parameter merges the outputs from all the input files.

## Text Tools
Collections of preprocessing steps that can be applied to any text file(s).

1. Remove Punctuations and other edits
2. Finding Repetitions
3. Filtering Phrases

To use this tool run:

```shell
python texttools.py -m --ConfigFilePath <PATH TO CONFIG FILE> --TranscriptFldrPath <PATH TO TRANSCRIPT FILES>
```

Notes:
1. The optional -m parameter merges the outputs from all the input files.

Configs:
The edits/changes made to the transcript files can be customized in the config file, here are the configs that you modify for your workflow (Please refer to the template_config.json file for reference):

1. 'removePunctuation' - removes punctuations, special characters, repeated black spaces
2. 'filterPhrases' - removes matched phrases from the input files
3. 'findRepetition' - finds the consecutive repetitions in the input text and reports them
4. 'outputSingleLine' - concats all the lines in the output files and outputs a single line in the file.
5. 'toLowerCase' - converts text to lower case
6. 'replaceHypens' - replaces one or two consecutive hypens with spaces


Both tools can be invoked using the python interpreter and passing required arguments/configs.