import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
import os
from collections import Counter


class InvertedIndexDictionary:

    def __init__(self, path_to_xml_dir):
        self.path_to_xml_dir = path_to_xml_dir
        self.dict = {}
        self.words_to_stop = set(stopwords.words('english'))
        self.words_to_stop.add("\n")

    def build_dictionary(self):
        files_list = [file for file in os.listdir(self.path_to_xml_dir) if file.endswith(".xml")]
        for file in files_list:
            paper_num, inverted_index_of_file = self.get_inverted_index_of_file(file)
            for word, count in inverted_index_of_file.items():
                if word in self.dict:
                    self.dict[word].append((paper_num, count))
                else:
                    self.dict[word] = [(paper_num, count)]

    # returns a dictionary containing word and their frequencies in file (takes words from title and
    def get_inverted_index_of_file(self, file):
        tree = ET.parse(self.path_to_xml_dir + "/" + file)
        root = tree.getroot()
        filtered_but_not_tokenized_words = []
        for record in root:
            paper_num = record.find("PAPERNUM")
            title = record.find("TITLE")
            body = record.find("ABSTRACT")
            if title is not None and body is not None:
                filtered_but_not_tokenized_words = [word for word in
                                                    " ".join([body.text, title.text]).replace("\n", ' ').split(' ') if
                                                    not word.lower() in self.words_to_stop]

            return paper_num.text, Counter(filtered_but_not_tokenized_words)
