#: Fields to fetch from book.show api call goodreads

BOOK_NODE_TAG = 'book'
BOOK_NODE_DESCENDENTS = [
    'id', 'title', 'isbn', 'image_url', 'small_image_url',
    'publication_year', 'publication_month', 'publication_day',
    'publisher', 'description', 'url', 'num_pages',
]

RATINGS_NODE_TAG = 'work'
RATINGS_DIST_TAG = 'rating_dist'
TEXT_REVIEWS_COUNT_TAG = 'text_reviews_count'

AUTHORS_NODE_TAG = 'authors'
AUTHORS_NODE_CHILD = 'author'
AUTHORS_NODE_CHILD_DESCENDENTS = ['id', 'name']

SIMILAR_BOOKS_NODE_TAG = 'similar_books'
SIMILAR_BOOKS_NODE_CHILD = 'book'
SIMILAR_BOOKS_NODE_CHILD_DESCENDENTS = ['id']
