from flask import jsonify, request

from . import biblio
from Bibliognost import get_logger
from ..modules.amazon import AmazonBot
from ..modules.goodreads import GoodReads, BookSearch, GoodReadsBot

logger = get_logger(__file__)


@biblio.route('/')
def index():
	book = GoodReads(request.args.get('book_id'))
	return jsonify(book.get_book_data())


@biblio.route('/search')
def search():
	results = BookSearch(request.args.get('q')).get_results()
	return jsonify(results)


@biblio.route('/amazon-reviews')
def amazon_reviews():
	try:
		amzn_reviews = AmazonBot(request.args.get('isbn')).get_reviews()
	except Exception as e:
		logger.exception(e)
		return jsonify([])
	else:
		return jsonify(amzn_reviews)


@biblio.route('/goodreads-review')
def goodreads_reviews():
	try:
		gr_reviews = GoodReadsBot(request.args.get('url'), 100).get_reviews()
	except Exception as e:
		logger.exception(e)
		return jsonify([])
	else:
		return jsonify(gr_reviews)
