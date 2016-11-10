#: Nodes to fetch from book.show api call from goodreads

CORE_DATA_NODE_TAG = 'book'
CORE_DATA_NODE_DESCENDENTS = [
    'id', 'title', 'isbn', 'image_url', 'small_image_url',
    'publication_year', 'publication_month', 'publication_day',
    'publisher', 'description', 'url', 'num_pages',
]

RATINGS_NODE_TAG = 'work'
RATINGS_DIST_TAG = 'rating_dist'

AUTHORS_NODE_TAG = 'authors'
AUTHORS_NODE_CHILD = 'author'
AUTHORS_NODE_CHILD_DESCENDENTS = ['id', 'name']

SIMILAR_BOOKS_NODE_TAG = 'similar_books'
SIMILAR_BOOKS_NODE_CHILD = 'book'
SIMILAR_BOOKS_NODE_CHILD_DESCENDENTS = ['id']

#: Nodes to fetch from search.book api call from goodreads

SEARCH_NODE_TAG = 'search'
RESULT_NODE_TAG = 'results'
WORK_NODE_TAG = 'work'

BEST_BOOK_NODE_TAG = 'best_book'
BEST_BOOK_NODE_DESCENDENTS = ['id', 'title', 'small_image_url']
