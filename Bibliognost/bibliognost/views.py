from flask import jsonify, request

from . import biblio
from Bibliognost import get_logger
from ..modules.amazon import AmazonBot
from ..modules.goodreads import GoodReads


logger = get_logger(__file__)


@biblio.route('/')
def index():
	book = GoodReads(request.args.get('book_id'))
	return jsonify(book.get_book_data())


@biblio.route('/search')
def search():
	results = BookSearch(request.args.get('q')).get_results()
	return jsonify(results)


@biblio.route('/reviews/<isbn>')
def reviews(isbn):
	try:
		amazon_reviews = AmazonBot(isbn).get_reviews()
	except Exception as e:
		logger.exception(e)
		return jsonify([])
	else:
		return jsonify(amazon_reviews)
