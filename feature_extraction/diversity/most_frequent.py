# scripts adapted from https://github.com/dimitarsh1/BiasMT/tree/main/scripts/diversity

# example call: python most_frequent.py -f ~/switchdrive/IMAGINE_files/chatGPT/project_2/final_files_simple_prompt/20min/human/2022-«Der-Hund-hat-fast-ihren-Arm-und-ihr-Bein-abgerissen»_507_de.txt 

import argparse
import os
import sys
import csv
from nltk.probability import FreqDist

vocs = "freq_voc/"


def main():
    ''' main function '''
    # read argument - file with data
    parser = argparse.ArgumentParser(description='Saves a list of the most frequent tokens of each given file.')
    parser.add_argument('-f', '--files', required=True,
                        help='the files to read (min 1).', nargs='+')

    args = parser.parse_args()

    sentences = {}

    system2 = ""

    metrics_bs = {}

    # 1. read all the file
    for textfile in args.files:

        # system = os.path.basename(os.path.dirname((os.path.dirname(textfile))))
        system = os.path.splitext(os.path.basename(textfile))[0]

        # this path will indicate human/machine in freq_voc
        system2 = os.path.basename(os.path.dirname(textfile))

        sentences[system] = []

        with open(textfile, 'r') as ifh:
            # ! Spacy UDPIPE crashes if we keep also empty lines
            sentences[system] = [s.strip() for s in ifh.readlines() if s.strip()]

    # 2. Compute overall metrics
    for syst in sentences:
        # create Frequency Dictionary
        print(syst)
        # our text is already tokenized. We merge all sentences together
        fdist = FreqDist(" ".join(sentences[syst]).split())
        # and create one huge list of tokens.

        with open(os.path.join(vocs, f"{system2}_{syst}.freq_voc"), "w") as oF:
            oF.write("\n".join([w + "\t" + str(c) for (w, c) in fdist.most_common()]))
    sys.exit("Done")


if __name__ == "__main__":
    main()