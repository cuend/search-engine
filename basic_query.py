import index_constructor


def formatQuery(query):
    terms = []
    # tokenize text using the same rules as the tokenize function
    alnum = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    for word in index_constructor.re.findall(r'\w+', query):
        word = word.lower()
        word = ''.join([c if c in alnum else ' ' for c in word])
        terms.extend(word.split())

    index_constructor.remove_stopwords(terms)

    return terms


def search_index(query):
    # connect to SQLite database
    conn = index_constructor.sqlite3.connect('inverted_index.db')
    c = conn.cursor()

    # split query into terms
    terms = formatQuery(query)

    # retrieve term ids from index
    term_ids = []
    for term in terms:
        c.execute('SELECT term_id FROM terms WHERE term = ?', (term,))
        result = c.fetchone()
        if result:
            term_ids.append(result[0])

    # retrieve matching document ids and tf-idf scores
    doc_scores = index_constructor.defaultdict(float)
    for term_id in term_ids:
        c.execute(
            'SELECT doc_id, tf_idf FROM postings WHERE term_id = ?', (term_id,))
        results = c.fetchall()
        for result in results:
            doc_id = result[0]
            tf_idf = result[1]
            doc_scores[doc_id] += tf_idf

    # retrieve URLs of top 20 documents
    top_docs = sorted(doc_scores.items(),
                      key=lambda x: x[1], reverse=True)[:20]
    doc_urls = []
    for doc_id, _ in top_docs:
        c.execute('SELECT url FROM documents WHERE doc_id = ?', (doc_id,))
        result = c.fetchone()
        if result:
            doc_urls.append(result[0])

    # close connection to database
    conn.close()

    return doc_urls
