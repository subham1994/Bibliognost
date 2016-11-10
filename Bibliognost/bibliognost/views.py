from flask import jsonify, request
from ..modules.goodreads import GoodReads
from . import biblio


@biblio.route('/')
def index():
	book = GoodReads(request.args.get('book_id'))
	return jsonify(book.get_book_data())

@biblio.route('/search')
def search():
	results = BookSearch(request.args.get('q')).get_results()
	return jsonify(results)
