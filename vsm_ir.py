import sys
from collections import Counter

from InvertedIndexDictionary import InvertedIndexDictionary


def create_index():
    input_files_path = sys.argv[2] if sys.argv[2].endswith("/") else sys.argv[2] + "/"
    inverted_index = InvertedIndexDictionary(input_files_path)
    inverted_index.build_inverted_index()
    inverted_index.save_data_to_files()


def query():
    pass
    # TODO: hadar implements this


if __name__ == '__main__':
    if sys.argv[1] == "create_index":
        create_index()
    if sys.argv[2] == "query":
        query()
