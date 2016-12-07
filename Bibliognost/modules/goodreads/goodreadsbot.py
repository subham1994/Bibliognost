import asyncio
import selectors
import time
from collections import Counter

import aiohttp
import math
from bs4 import BeautifulSoup
from bs4.element import Tag

from Bibliognost import get_logger

logger = get_logger('goodreadsbot')


class GoodReadsBot(object):
	def __init__(self, url, num_reviews):
		"""
		initialize goodreads review bot.

		:param url: a valid goodreads book url
		:type url: str
		:param num_reviews: total number of reviews for that book
		:type num_reviews: int
		"""
		self.url = url
		self.num_reviews = num_reviews
		self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}

	async def _create_soup(self, session):
		"""
		Makes async request to the server and parses the
		responses using lxml tree builder

		:param session: aiohttp session object to fetch url
		:type session: aiohttp.client.ClientSession
		:return: bs4.BeautifulSoup object
		"""
		async with session.get(self.url) as response:
			html = await response.text()
		return BeautifulSoup(html, 'lxml')

	async def _fetch_dynamically_loaded_reviews(self):
		pass

	def _get_review_body(self, review_body_span):
		"""
		returns the body of review.

		:param review_body_span: span element contiaining the review body
		:type review_body_span: bs4.element.Tag
		:return: `str`, the body of review
		"""
		for child in review_body_span.children:
			if type(child) is Tag and child.name == 'a':
				text_id = child.get('data-text-id')
				review_body = review_body_span.find('span', attrs={'id': 'freeText{id}'.format(id=text_id)}).contents
				break
		else:
			review_body = review_body_span.find('span').contents
		return ' '.join(list(map(str, review_body)))

	def _get_rating(self, static_star_node):
		"""
		return the rating for the book

		:param static_star_node: node containing all the star spans
		:type static_star_node: bs4.element.Tag
		:return: `int`, rating for the book on a scale of 5
		"""
		#: first create a list of span, each containg a single star rating.
		#: If the class name of span contains `p10` it means 1, `p0` is 0.
		#: The structure of each span is like <span class="staticStar p10" ..>
		#: or <span class="staticStar p0"..></span>. since the scale of rating
		#: is 5, `static_star_node.contents` is going to create a list having
		#: 5 span nodes. Simply count the number of `p10` span to the get the rating.

		#: The function being mapped takes each span node from list, extracts the
		#: class attr from it, which returns list having structure ["staticStar" "p10"].
		#: Get the second element from list to get `p10` or `p0`. Now the list is
		#: flattened to ["p10", ..., "p0"] structure. simply return the count of `p10`.
		if static_star_node is None:
			return 0
		return Counter(list(map(lambda span: span.get('class')[1], static_star_node.contents))).get('p10', 0)

	def _build_review_dict(self, review_header, review_body):
		"""
		builds a single review

		:param review_header: node containing header info of review i.e. title, author, etc
		:type review_header: bs4.element.Tag
		:param review_body: node containing body of review
		:type review_body: bs4.element.Tag
		:return: dict
		"""
		review = dict()
		review['author'] = review_header.find('a', class_='user').getText()
		review['date'] = review_header.find('a', class_='reviewDate createdAt right').getText()
		review['rating'] = self._get_rating(review_header.find('span', class_=' staticStars'))
		review['body'] = self._get_review_body(review_body.find('span', class_='readable'))
		review['title'] = review.get('body')[:50] + '...'
		return review

	def _build_reviews_list(self, book_reviews_child_nodes):
		"""
		builds the list of all reviews available on a page

		:param book_reviews_child_nodes: node containing every review node on the page
		:type book_reviews_child_nodes: bs4.element.Tag
		:return: list containing all the reviews available on current page
		"""
		reviews = []
		for child in book_reviews_child_nodes:
			if type(child) is Tag and ' '.join(child.get('class', '')) == 'friendReviews elementListBrown':
				review_header = child.find('div', class_='reviewHeader uitext stacked')
				review_body = child.find('div', class_='reviewText stacked')
				try:
					reviews.append(self._build_review_dict(review_header, review_body))
				except Exception as e:
					logger.exception(e)
		return reviews

	async def build_reviews_from_soup(self, session):
		soup = await self._create_soup(session)
		book_reviews_node = soup.find('div', attrs={'id': 'bookReviews'})
		assert book_reviews_node
		book_reviews_child_nodes = book_reviews_node.children
		logger.info('Fetching page')
		return self._build_reviews_list(book_reviews_child_nodes)

	def get_reviews(self):
		"""
		Fetches the first page first, then makes
		an asynchronous request to remaining pages
		and waits until all the ajax requests have
		completed. Once all the reviews are loaded,
		parses the html for each page to get the
		reviews in desired format.

		:return: `list[dict]` which is json serializable
		"""
		if not self.num_reviews:
			logger.info('No reviews available')
			return []
		#: goodreads shows a max of 30 reviews per page
		#: and we already know the total number of reviews.
		#: We can take advantage of this info to calculate
		#: the total number of review pages. It can simply be
		#: formulated as:
		#:     num_pages = ceil(num_reviews / 30), if num_reviews > 0
		num_pages = math.ceil(self.num_reviews / 30)
		selector = selectors.SelectSelector()
		loop = asyncio.SelectorEventLoop(selector)
		asyncio.set_event_loop(loop)
		start = time.time()
		with aiohttp.ClientSession() as session:
			reviews_from_first_page = loop.run_until_complete(
				asyncio.gather(self.build_reviews_from_soup(session), return_exceptions=True)
			)
		logger.info('Fetched reviews from {p} page(s) in: {t} s'.format(t=time.time() - start, p=num_pages))
		filtered_reviews = []
		for index, reviews_list in enumerate(reviews_from_first_page):
			if isinstance(reviews_list, Exception) or not reviews_list:
				cause = 'request blocked by remote server' if not reviews_list else reviews_list
				logger.warning('Failed to get result for page: {p}, cause={e}'.format(p=index + 1, e=cause))
			else:
				for review in reviews_list:
					filtered_reviews.append(review)
		return filtered_reviews
