import argparse
import os
from tqdm import tqdm
from multiprocessing import Pool

from pypdf import PdfReader
from pdfminer.converter import HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from io import BytesIO, StringIO
from langdetect import detect as detect_lang


def file_path(string):
    """Check if string is a valid filepath"""
    if os.path.exists(string):
        return string
    else:
        raise NotADirectoryError


def convert_pdf_to_txt(pdf_path):
    output_string = StringIO()
    with open(pdf_path, 'rb') as fp:
        resource_manager = PDFResourceManager()
        converter = TextConverter(resource_manager, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(fp, check_extractable=True):
            interpreter.process_page(page)
        converter.close()

    content = output_string.getvalue()
    output_string.close()

    return content


def pdfreader(filename):
    """using pyPDF to get the text from a pdf"""
    reader = PdfReader(filename)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def get_language(filename):
    """detect the language of a pdf file"""
    text = pdfreader(filename)
    return detect_lang(text)

def get_language_overview(folder):
    files = [os.path.join(folder, file) for file in os.listdir(folder)]
    lang_dict = {}

    # for file in tqdm(files):
    #     text = pdfreader(file)
    #     lang = detect_lang(text)
    #     if lang in lang_dict:
    #         lang_dict[lang] += 1
    #     else:
    #         lang_dict[lang] = 1
    # return lang_dict


    with Pool(processes=8) as pool:
        results_iter = pool.imap_unordered(get_language, files)
        for lang in tqdm(results_iter, total=len(files)):
            if lang in lang_dict:
                lang_dict[lang] += 1
            else:
                lang_dict[lang] = 1

    return lang_dict

def testrun(testfile, outfile, testfunc):
    """for testing different methods to convert pdfs"""
    content = testfunc(testfile)
    with open(outfile, "w", encoding="utf-8") as outfile:
        outfile.write(content)

def test():
    """calling the testrun"""
    testfile = "C:/Users/nik_b/Documents/UZH/student_assistant/Zora/data/linguistics_and_language/downloads/2006-3445b27b230257a81f9d6326373e94de9a00abfc.pdf"

    testrun(testfile, "pdfminer_test3.txt", convert_pdf_to_txt)
    testrun(testfile, "pypdf_test3.txt", pdfreader)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type=str, choices=["lang_overview", "extract"], help="lang_overview gives ")
    parser.add_argument("infolder", type=file_path)
    args = parser.parse_args()

    if args.mode == "lang_overview":

        print(get_language_overview(args.infolder))


