import index_constructor
import basic_query

# main program
if __name__ == "__main__":
    # create inverted index if not yet created (it should be ready bc it takes a long time)
    # index_constructor.create_index()

    while True:
        query = input(
            "What would you like to search for? (type 'quit' to exit) ")
        if query.lower() == 'quit':
            break
        print("Search results for:", query.lower())
        urls = basic_query.search_index(query)
        for url in urls:
            print(url)

    print("Goodbye!")
