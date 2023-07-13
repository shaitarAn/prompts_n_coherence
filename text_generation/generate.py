import os
import requests
import json
import re
from helper import Tokenizer, parse_filename
import argparse
from tqdm import tqdm
from datetime import datetime
import time



class OpenAiModels:

    def __init__(self, model_name:str, api_key, org_id=None):
        self.api_key = api_key
        self.model_name = model_name

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        if org_id:
            self.headers["OpenAI-Organization"] = org_id

    def generate(self, prompt, temp=0.7):

        if self.model_name == "gpt-3.5-turbo":
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': temp,
            }

            for i in range(10):
                response = requests.post('https://api.openai.com/v1/chat/completions', headers=self.headers, data=json.dumps(data))
                if response.status_code == 200:
                    result = response.json()

                    if not "error" in result:
                        return result["choices"][0]["message"]["content"]  # result["choices"][0]["text"]
                    else:
                        print("\n\nOpenAI error: ", result["error"])

                elif response.status_code < 500:
                    print("\n\nHTTP ERROR:", response.status_code)
                    try:
                        error_dict = response.json()
                        print(error_dict)
                    except:
                        pass
                    exit()


                else:  # Serverside errors (<500)
                    time.sleep(1.2 ** i)  # exponential increase between failed requests, last request waits for approx. 5 seconds

            print("##########\nGeneration failed")
            print("\n\nHTTP ERROR:", response.status_code)
            try:
                print(f"Reason: {response.reason}")
            except:
                pass
            exit()


def truncate_texts(machine_text, human_text, tokenizer):

    machine_text_tok_list = tokenizer.token_list(machine_text)
    human_text_tok_list = tokenizer.token_list(human_text)

    min_length = min(len(machine_text_tok_list), len(human_text_tok_list))

    return " ".join(machine_text_tok_list[:min_length]), " ".join(human_text_tok_list[:min_length]), min_length


def generate(model, prompt, lang, min_len = 500):
    
    # print(f"\ngenerating, iteration num: {iter}", end="\r")
    tokenizer = Tokenizer(lang)
    text = model.generate(prompt)
    num_toks, _ = tokenizer.tokenize_text(text)

    while num_toks < min_len:
        
        
        prompt += text
        text += model.generate(prompt)
        num_toks, _ = tokenizer.tokenize_text(text)

    # print("", end="\r\r")
    return text


def write_texts(machine, human, filename, outfolder):
    """ write the two text file in two folders "machine" and "human"""
    outfolders = [f"{outfolder}/machine", f"{outfolder}/human"]
    for text, folder in zip([machine, human], outfolders):
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = f"{folder}/{filename}"
        with open(filepath, "w", encoding="utf-8") as outfile:
            outfile.write(text)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=str, choices=["gpt-3.5-turbo"], help="OpenAI model to use")
    parser.add_argument("source_file", type=str, help="Filepath of the JSON file with the human texts in following format:"
                                                        "{filename:{'title': '...', 'prompt': '...', 'text': '...'}}")
    parser.add_argument("lang", type=str, choices=["de", "en"], help="language")
    parser.add_argument("--prompt_file", type=str, default="", help="File containing the prompt. The prompt can include placeholders"
                                                        "<title> and <prompt> for including text from the human files.")

    parser.add_argument("--outfolder", type=str, default="")
    parser.add_argument("--start_from", type=int, default=0, help="If part of the files are already done, this is the one to start from")
    args = parser.parse_args()
    model_name = args.model
    source_file = args.source_file
    lang = args.lang
    prompt_file = args.prompt_file
    outfolder = args.outfolder
    start_from = args.start_from

    # open the specified source file
    with open(source_file, "r", encoding="utf-8") as infile:
        source_dict = json.load(infile)

    # Open the prompt file, if specified, otherwise apply a simple prompt
    if prompt_file:
        with open(prompt_file, "r", encoding="utf-8") as infile:
            prompt_source = infile.read()
    else:
        if lang == "en":
            prompt_source = "Complete the following text:\n<title>\n\n<prompt>"
        if lang == "de":
            prompt_source = "Vervollständige den folgenden text:\n<title>\n\n<prompt>"

    # Initialize the specified model
    api_key = os.getenv("OPENAI_KEY")
    org_id = os.getenv("ORG_ID")
    model = OpenAiModels(model_name, api_key, org_id)

    # Initialize a tokenizer with the specified language
    tokenizer = Tokenizer(lang)

    # make default output directory
    if not outfolder:
        outfolder = "output" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    # Go over all the documents
    for filename in tqdm(list(source_dict.keys())[start_from:]):

        year, title, _, lang = parse_filename(filename)

        prompt = re.sub("<title>", source_dict[filename]["title"], prompt_source)
        prompt = re.sub("<prompt>", source_dict[filename]["prompt"], prompt)
        machine_text = generate(model, prompt, lang)

        # truncate and tokenize the texts
        machine, human, num_toks = truncate_texts(machine_text, source_dict[filename]["text"], tokenizer)


        new_filename = f"{year}-{title}_{num_toks}_{lang}.txt"
        write_texts(machine, human, new_filename, outfolder)


