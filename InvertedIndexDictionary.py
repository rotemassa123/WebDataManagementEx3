import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
import os
from collections import Counter
import json

TERM_FREQUENCY = "term_frequency"
DOCUMENT_FREQUENCY = "document_frequency"
DOCUMENT_LENGTHS = "document_lengths"

class InvertedIndexDictionary:

    def __init__(self, path_to_xml_dir):
        self.path_to_xml_dir = path_to_xml_dir
        self.term_frequency = {}
        self.document_frequency = {}
        self.doc_len_dict = {}
        self.words_to_stop = set(stopwords.words('english'))
        self.words_to_stop.add("\n")
        self.count_of_docs = 0

    def build_inverted_index(self):
        files_list = [file for file in os.listdir(self.path_to_xml_dir) if file.endswith(".xml")]
        for file in files_list:
            count_of_docs_in_file, counter_dict_for_file, doc_len_dict_for_file = self.get_inverted_index_of_file(file)
            self.count_of_docs += count_of_docs_in_file
            self.merge_two_freq_dicts(self.term_frequency, counter_dict_for_file)
            self.doc_len_dict.update(doc_len_dict_for_file)

        for word in self.term_frequency:
            self.document_frequency[word] = len(self.term_frequency[word]) / self.count_of_docs

    # returns a dictionary containing word and their frequencies in file (takes words from title and
    def get_inverted_index_of_file(self, file):
        tree = ET.parse(self.path_to_xml_dir + "/" + file)
        root = tree.getroot()
        counter_dict_for_file = {}
        doc_len_dict_for_file = {}
        count_of_docs_in_file = len(root.findall("RECORD"))
        for record in root:
            filtered_but_not_tokenized_words = []
            counter_dict_for_doc = {}
            paper_num = record.find("PAPERNUM")
            title = record.find("TITLE")
            body = record.find("ABSTRACT")

            if title is not None and body is not None:
                words = " ".join([body.text, title.text]).replace("\n", ' ').split(' ')
                filtered_but_not_tokenized_words = [word for word in words if not word.lower() in self.words_to_stop]
                doc_len_dict_for_file[paper_num.text] = len(words)

            term_freq_dict_for_doc = Counter(filtered_but_not_tokenized_words)
            for word, count in term_freq_dict_for_doc.items():
                counter_dict_for_doc[word] = (paper_num.text, count)

            self.merge_two_freq_dicts(counter_dict_for_file, counter_dict_for_doc)

        return count_of_docs_in_file, counter_dict_for_file, doc_len_dict_for_file

    @staticmethod
    def merge_two_freq_dicts(dict1, dict2):
        for word in dict2:
            if word in dict1:
                dict1[word] += dict2[word]
            else:
                dict1[word] = dict2[word]


