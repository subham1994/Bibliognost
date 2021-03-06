import itertools
import multiprocessing

from flask import render_template, jsonify, request

from Bibliognost import get_logger
from . import biblio
from ..modules.amazon import AmazonBot
from ..modules.goodreads import GoodReads, BookSearch, GoodReadsBot
from ..modules.sent_analysis import fastClassifier

logger = get_logger(__file__)


@biblio.route('/')
def index():
	return render_template('base.html')


@biblio.route('/book/<book_id>')
def book_details(book_id):
	book = GoodReads(book_id)
	return render_template('book-details.html', book_details=book.get_book_data())


@biblio.route('/book-meta')
def book_meta():
	book_ids = request.args.get('book_ids').split(',')
	pool = multiprocessing.Pool()
	book_details_processes = [pool.apply_async(GoodReads(book_id).get_book_data) for book_id in book_ids]
	book_details = [book_detail.get() for book_detail in book_details_processes]
	return jsonify(book_details)


@biblio.route('/search')
def search():
	results = BookSearch(request.args.get('q')).get_results()
	return render_template('search-results.html', results=results)


def amazon_reviews(isbn):
	try:
		amzn_reviews = AmazonBot(isbn).get_reviews()
	except Exception as e:
		logger.exception(e)
		return []
	else:
		return amzn_reviews


def goodreads_reviews(url):
	try:
		gr_reviews = GoodReadsBot(url, 100).get_reviews()
	except Exception as e:
		logger.exception(e)
		return []
	else:
		return gr_reviews


@biblio.route('/reviews')
def reviews_with_sentiment():
	pool = multiprocessing.Pool()
	fetch_review_processes = [
		pool.apply_async(amazon_reviews, args=(request.args.get('isbn'),)),
		pool.apply_async(goodreads_reviews, args=(request.args.get('url'),))
	]
	amzn_reviews, gr_reviews = [reviews.get() for reviews in fetch_review_processes]
	review_texts = [review.get('body') for review in itertools.chain(amzn_reviews, gr_reviews)]
	sentiments = fastClassifier.predict_sentiment(review_texts)
	for idx, response in enumerate(itertools.chain(amzn_reviews, gr_reviews)):
		response['sentiment'] = float(sentiments[idx])
	return jsonify({'amazon': amzn_reviews, 'goodreads': gr_reviews, 'num_reviews': len(review_texts)})
