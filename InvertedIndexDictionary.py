import math
import xml.etree.ElementTree as ET

import nltk
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
import os
from collections import Counter
import json
from nltk.stem import PorterStemmer

OUTPUT_FILE = "output.json"


class InvertedIndexDictionary:

    def __init__(self, path_to_xml_dir):
        self.path_to_xml_dir = path_to_xml_dir
        self.dict = {}
        try:
            stop_words = set(stopwords.words("english"))
        except:
            nltk.download('stopwords')
            stop_words = set(stopwords.words("english"))

        self.words_to_stop = set(stopwords.words('english'))
        self.words_to_stop.add("\n")
        self.count_of_docs = 0

    def build_inverted_index(self):
        files_list = [file for file in os.listdir(self.path_to_xml_dir) if file.endswith(".xml")]
        term_frequency = {}
        log_inverted_document_frequency = {}
        len_by_doc_name = {}
        for file in files_list:
            count_of_docs_in_file, counter_dict_for_file, doc_len_dict_for_file = self.get_inverted_index_of_file(file)
            self.count_of_docs += count_of_docs_in_file
            self.merge_two_freq_dicts(term_frequency, counter_dict_for_file)
            len_by_doc_name.update(doc_len_dict_for_file)

        for word in term_frequency:
            log_inverted_document_frequency[word] = math.log2(self.count_of_docs / len(term_frequency[word]))

        self.dict = {"TF": term_frequency, "len_by_doc_name": len_by_doc_name, "IDF": log_inverted_document_frequency}

    # returns a dictionary containing word and their frequencies in file (takes words from title and
    def get_inverted_index_of_file(self, file):
        tree = ET.parse(self.path_to_xml_dir + "/" + file)
        root = tree.getroot()
        counter_dict_for_file = {}
        doc_len_dict_for_file = {}
        count_of_docs_in_file = len(root.findall("RECORD"))

        for record in root:
            counter_dict_for_doc = {}
            record_num = record.find("RECORDNUM")
            len_of_doc, words = self.get_tokenized_words_from_record(record)
            doc_len_dict_for_file[record_num.text] = len_of_doc
            term_freq_dict_for_doc = Counter(words)

            for word, count in term_freq_dict_for_doc.items():
                counter_dict_for_doc[word] = (record_num.text, count)
            self.merge_two_freq_dicts(counter_dict_for_file, counter_dict_for_doc)

        return count_of_docs_in_file, counter_dict_for_file, doc_len_dict_for_file

    def get_tokenized_words_from_record(self, record):
        text = ""
        title = record.find("TITLE")
        abstract = record.find("ABSTRACT")
        extract = record.find("EXTRACT")

        if title is not None:
            text += str(title.text)
        if abstract is not None:
            text = " ".join([text, str(abstract.text)])
        if extract is not None:
            text = " ".join([text, str(extract.text)])

        return self.get_tokenized_filtered_and_stemmed_words(text)

    def get_tokenized_filtered_and_stemmed_words(self, text):
        tokenizer = RegexpTokenizer(r'\w+')
        porter_stemmer = PorterStemmer()

        words = tokenizer.tokenize(text.lower())
        filtered_words = [word for word in words if not word in self.words_to_stop]

        return len(words), filtered_words


    @staticmethod
    def merge_two_freq_dicts(dict1, dict2):
        for word in dict2:
            if word in dict1:
                dict1[word] += dict2[word]
            else:
                dict1[word] = dict2[word]

    def save_data_to_files(self, path=""):
        with open(path + OUTPUT_FILE, "w") as outfile:
            json.dump(self.dict, outfile)

    def load_data_from_files(self, path=""):
        with open(path + OUTPUT_FILE) as json_file:
            dict = json.load(json_file)

        return dict
