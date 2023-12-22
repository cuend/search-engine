# index construciton will be done within this file

import json
from collections import defaultdict
import os
import re
from lxml import html
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer

# stop words to be removed
ENG_STOPWORDS = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off',
                 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

# functions from project 2 that will help tokenize each url


def remove_stopwords(words):
    return [word for word in words if word.lower() not in ENG_STOPWORDS]


def tokenize(html_content):
    wordlist = []
    tree = html.fromstring(html_content)

    # extract text from HTML content
    text = tree.text_content()

    # tokenize text for alphanum characters and standardize capitalization to lowercase
    alnum = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    for word in re.findall(r'\w+', text):
        word = word.lower()
        word = ''.join([c if c in alnum else ' ' for c in word])
        wordlist.extend(word.split())

    return wordlist


def create_index():
    # connect to SQLite database
    conn = sqlite3.connect('inverted_index.db')
    c = conn.cursor()

    # create tables
    # documents table that uses the '0/0' naming convention as the doc_id
    # and the stores the associated url
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                (doc_id TEXT PRIMARY KEY, url TEXT)''')

    # terms table that assigns an integer term_id to a unique term found
    # in the corpus
    c.execute('''CREATE TABLE IF NOT EXISTS terms
                (term_id INTEGER PRIMARY KEY, term TEXT)''')

    # postings list for the associated term via their term_id, the associated
    # doc_id, frequency of term in document, and tf-idf score
    c.execute('''CREATE TABLE IF NOT EXISTS postings
                (term_id INTEGER, doc_id TEXT, frequency INTEGER,
                indices TEXT, tf_idf REAL,
                FOREIGN KEY(term_id) REFERENCES terms(term_id),
                FOREIGN KEY(doc_id) REFERENCES documents(doc_id))''')

    # index documents (simply move from bookkeeping json file to the database)
    # and create a  local doc_index to process the actual content in files
    doc_folder = 'WEBPAGES_RAW'
    doc_index = {}
    with open('WEBPAGES_RAW/bookkeeping.json', 'r') as f:
        bookkeeping = json.load(f)
    for doc_name in bookkeeping:
        doc_id = doc_name
        url = bookkeeping[doc_name]
        with open(os.path.join(doc_folder, doc_id), 'r') as f:
            html_content = f.read()
            try:
                # tokenize and remove stop words
                wordlist = remove_stopwords(tokenize(html_content))
                text = ' '.join(wordlist)
                # insert document into database
                c.execute('INSERT INTO documents VALUES (?, ?)', (doc_id, url))
                doc_index[doc_id] = text
            except:
                continue

    # calculate tf-idf scores using scikit-learn
    vectorizer = TfidfVectorizer()
    tf_idf_matrix = vectorizer.fit_transform(doc_index.values())

    # index terms and postings
    term_index = {}
    postings = defaultdict(list)

    for i, term in enumerate(vectorizer.get_feature_names_out()):
        term_id = i
        term_index[term] = term_id

        # initialize document frequency (df) for current term
        df = 0

        # process each document
        for j, doc_id in enumerate(doc_index.keys()):
            tf_idf = tf_idf_matrix[j, i]

            # check if the term is present in the document
            if term in doc_index[doc_id]:
                df += 1
                matches = [(match.start(), match.end()) for match in re.finditer(
                    r'\b{}\b'.format(term), doc_index[doc_id])]
                postings[doc_id].append({'term_id': term_id, 'freq': len(
                    matches), 'indices': matches, 'tf_idf': tf_idf})

        # insert term and df into database
        c.execute('INSERT INTO terms VALUES (?, ?)', (term_id, term))

        # insert postings into database
        for doc_id, doc_postings in postings.items():
            for posting in doc_postings:
                if posting['term_id'] == term_id and posting['freq'] > 0:
                    c.execute('INSERT INTO postings VALUES (?, ?, ?, ?, ?)', (term_id,
                              doc_id, posting['freq'], str(posting['indices']), posting['tf_idf']))

    # commit changes and close connection
    conn.commit()
    conn.close()
