import sys
from collections import Counter

from InvertedIndexDictionary import InvertedIndexDictionary

if __name__ == '__main__':
    dict = InvertedIndexDictionary("xml_input_files")
    dict.build_dictionary()
    print(dict.dict)
