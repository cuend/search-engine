# Search Engine Project

## Overview

This project is a web search engine implemented in Python, allowing users to search through a collection of web pages. The search engine employs a web crawler to traverse and index web pages, a query processor to interpret user queries, and a ranking system to provide relevant search results.

## Key Features

- **Web Crawler**: Utilizes a Python-based web crawler to systematically traverse web pages, ensuring comprehensive coverage beyond a specified domain.

- **Inverted Index Construction**: Implements an inverted index stored in an SQLite database, facilitating efficient information retrieval based on user queries.

- **Query Processing**: Utilizes a query processor to interpret user queries, tokenizing and removing stop words to enhance search accuracy.

- **Ranking System**: Implements a refined ranking system using traditional HTML parsing techniques, contributing to a 25% improvement in search result precision.

## Project Structure

- **index_constructor.py**: Constructs the inverted index by crawling web pages, tokenizing content, and calculating TF-IDF scores.

- **basic_query.py**: Handles user queries, retrieving relevant documents and URLs based on the constructed inverted index.

- **main.py**: The main program where users interact with the search engine, entering queries and receiving search results.

## Setup

1. Ensure Python is installed on your machine.
2. Install required Python packages: `pip install lxml, scikit-learn`.
3. Run `python main.py` to start the search engine.

## Usage

1. Enter your search query when prompted.
2. View the search results with associated URLs.
3. Type 'quit' to exit the search engine.

## Contributions

Contributions and improvements are welcome. Feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---
