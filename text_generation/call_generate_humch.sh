#!/bin/bash

## without parameters

model="gpt-4" #"gpt-4-turbo-2024-04-09" #gpt-3.5-turbo-16k, gpt-4

outfolder="../data_2409_gpt4" # in this folder subfolders task/corpus/system will be created

# make sure the folder exists
mkdir -p $outfolder

infolder="../data_collection/100_files_json/"  # Folder with all the JSON for generation

# echo $OPENAI_API_KEY
language="de"

if [ "$language" == "de" ]; then
    prompt_file="prompts_humch_german.json"

    corpora=("pubmed_de" "20min") 
else
    prompt_file="prompts_humch_english.json"

    corpora=("pubmed_en" "cnn") 
fi

for corpus in "${corpora[@]}";do

    echo "Running $corpus"

    python3 generate_personas.py $model -c $corpus -i $infolder -o $outfolder -p $prompt_file

done