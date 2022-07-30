import sys #to receive input from command line arguments
import os
import traceback # for tracing errors (not sure we need it)
import time # to measure running time
import xml.etree.ElementTree as ET
import nltk
import math
import json
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer

dictionary = {} # This dictionary holds all the words, the tf-idf for each file for every word.
words_per_file = {} # This dictionary holds the number of words after tokenization for every file. (key = file_name : value = integer)
query_dictionary = {}
document_reference = {} # This dictionary holds the length of all document vectors
corpus = {} # This dictionary holds the words dictionary ("dictionary") and the document_reference (dictionary of all files and their lengths)

            ### PART 1: Inverted Index and TF-IDF score. ###

# Add document to document_reference (key = document_id : value = 0)
def insert_to_document_reference(record_id):
    if record_id not in document_reference:
        document_reference[record_id] = 0


# Extract the desired text from file, tokenize the text, filter stop words and stemming.
def extract_words(filename):
    try:
        stop_words = set(stopwords.words("english"))
    except:
        nltk.download('stopwords')
        stop_words = set(stopwords.words("english"))

    tokenizer = RegexpTokenizer(r'\w+')
    ps = PorterStemmer()
    xml_tree = ET.parse(filename)
    root = xml_tree.getroot()
    for child in root.findall("./RECORD"):  #extracts all the text from file.

        #Initialize...
        text = ""
        filtered_text = []

        #Calculating...
        for entry in child:
            if entry.tag =="RECORDNUM":
                record_id = int(entry.text)
                insert_to_document_reference(record_id)
            if entry.tag == "TITLE":
                text += str(entry.text)+" "
            if entry.tag == "ABSTRACT":
                text += str(entry.text)+" "
            if entry.tag == "EXTRACT":
                text += str(entry.text)+" "

        text = text.lower()
        text = tokenizer.tokenize(text)  #tokenize and filter punctuation.
        filtered_text = [word for word in text if not word in stop_words]  #remove stop words.

        for i in range(len(filtered_text)):  #stemming
            filtered_text[i] = ps.stem(filtered_text[i])

        update_dictionary(filtered_text, record_id)
        words_per_file[record_id] = len(text)


# Insert to dictionary all the words that appear in the file: 'file_name'
def update_dictionary(text, file_name):
    for word in text:
        if word in dictionary: # NOTE: if the word is in the dictionary there must be a nested dictionary in its value.
            if dictionary.get(word).get(file_name): # check if exists a key with the name of the file in the nested dictionary.
                dictionary[word][file_name]["count"] += 1 # increment the number of the occurrences of the word in the nested dictionary file_name value.
            else: # in case there is not an existing key with the name of the file (file_name) in the nested dictionary.
                dictionary[word].update({file_name : {"count" : 1 , "tf_idf" : 0}})
        else:
            dictionary[word] = {file_name : {"count" : 1 , "tf_idf" : 0}}


# Calculate the tf-idf score of each word to each file and add current word per document score value to document_reference
def calculate_tf_idf(amount_of_docs):
    for word in dictionary:
        for file in dictionary[word]:
            tf = dictionary[word][file].get('count')/words_per_file.get(file)
            idf = math.log2(amount_of_docs / len(dictionary[word]))
            dictionary[word][file]["tf_idf"] = tf*idf

            #Incrementing length of current file by (idf*tf)^2:
            document_reference[file] += (tf*idf*tf*idf)

# Sqaure root of document vectors lengths
def root_documents_lengths():
    for file in document_reference:
        document_reference[file] = math.sqrt(document_reference[file])

# Build inverted index with tf-idf score to all the words from the given files.
def create_index():
    input_dir = sys.argv[2]
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xml"):
            file=input_dir+"/"+file_name
            extract_words(file)
    amount_of_docs = len(document_reference)
    # Adding tf-idf weights for each word for each document AND calculating document vectors lengths (squared)
    calculate_tf_idf(amount_of_docs)

    # Sqaure root of lengths in document_reference
    root_documents_lengths()

    # Add dictionary and document_reference to corpus
    corpus["dictionary"] = dictionary
    corpus["document_reference"] = document_reference

    inverted_index_file = open("vsm_inverted_index.json", "w")
    json.dump(corpus, inverted_index_file, indent = 8)
    inverted_index_file.close()


            ### PART 2: Information Retrieval given a query. ###

# Create hashmap of dj * q for all documents that include words from query
def documents_vectors_for_cossim(query_map, inverted_index):
    documents_vectors = {}
    for token in query_map:
        w = query_map[token] # w = token's tf-idf (in query)
        if inverted_index.get(token) != None:
            for doc in inverted_index[token]:
                if doc not in documents_vectors:
                    documents_vectors[doc] = 0

                documents_vectors[doc] += (inverted_index[token][doc]["tf_idf"] * w)

    return documents_vectors

# Create sorted list of relevant documents by cosSim
def results(query_map, inverted_index, document_reference):
    results = []

    # Calc query vector length
    query_length = 0
    for token in query_map:
        query_length += (query_map[token]*query_map[token])
    query_length = math.sqrt(query_length)

    documents_vectors = documents_vectors_for_cossim(query_map, inverted_index)
    for doc in documents_vectors:
        doc_query_product = documents_vectors[doc]
        doc_length = document_reference[doc]
        cosSim = doc_query_product / (doc_length * query_length)
        results.append((doc, cosSim))

    # Sort list by cosSim
    results.sort(key = lambda x: x[1], reverse=1)
    return results

# Lowercase the string question input, tokenize and eliminate puctuations, filter stopwords, stem.
def simplify_query_input():
    try:
        question = sys.argv[3].lower()
    except:
        return False
    stop_words = set(stopwords.words("english"))
    tokenizer = RegexpTokenizer(r'\w+')
    ps = PorterStemmer()
    question = tokenizer.tokenize(question) #tokenize and filter punctuation.
    filtered_question = [word for word in question if not word in stop_words]  #remove stop words.
    for i in range(len(filtered_question)): #stemming
        filtered_question[i] = ps.stem(filtered_question[i])
    return filtered_question


# Calculate query's tf-idf score.
def query_tf_idf(query, dictionary, amount_of_docs):
    query_length = len(query)
    for i in query: #'i' is a word i in file, *NOT AN INDEX!*
        count = 0
        if query_dictionary.get(i) == None: #Continue processing if the word i is not in dictionary already.
            for j in query: #'j' is a word j in file, *NOT AN INDEX!*
                if i == j:
                    count += 1
            tf = (count / query_length)
            if dictionary.get(i) != None:
                idf = math.log2(amount_of_docs / len(dictionary.get(i)))
            else:
                idf = 0
            query_dictionary.update({str(i) : tf*idf})


# Retrieve information given a question and an inverted index.
def query():
    index_path = sys.argv[2]

    # Handle wrong index_path from user
    try:
        json_file = open(index_path,"r") # Open json file to read from it.
    except:
        print("Could not open given path of index: ",index_path, "\nIt is possible that the path is wrong or that the index json file was not created yet.")
        return

    corpus = json.load(json_file) # Insert the json file to the global dictionary.
    inverted_index = corpus["dictionary"]
    document_reference = corpus["document_reference"]
    amount_of_docs = len(document_reference)
    json_file.close()

    query = simplify_query_input() # Manipulate the string query to list of words without stopwords and with stemming.

    if query == False:
        print("Query question is missing from input.")
        return

    query_tf_idf(query, inverted_index,amount_of_docs) # Calculate the tf_idf of the words in query and insert to global variable 'query_dictionary'.

    all_relevant_docs = results(query_dictionary, inverted_index, document_reference)

    f = open("ranked_query_docs.txt","w")
    for i in range(0, len(all_relevant_docs)):
        if(all_relevant_docs[i][1] >= 0.075):
            f.write(all_relevant_docs[i][0] + "\n")

    f.close()



# Call method 'create_index' or 'query' depends on command line arguments input.

def main():
    if (sys.argv[1] == "create_index"):
        create_index()

    elif (sys.argv[1] == "query"):
        query()

    else:
        print("Illegal Input! \n please insert correct instruction  :)")


main()
