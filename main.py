import sys
from collections import Counter

from InvertedIndexDictionary import InvertedIndexDictionary

def get_dict_diffs(dict1, dict2):
    set1 = set(dict1.items())
    set2 = set(dict2.items())
    print(set1 ^ set2)

if __name__ == '__main__':
    inverted_index = InvertedIndexDictionary("xml_input_files")
    inverted_index.build_inverted_index()
    inverted_index.save_data_to_files("output_files/")
    dict = inverted_index.load_data_from_files("output_files/")
