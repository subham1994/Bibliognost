import asyncio
import selectors
import time

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag

from Bibliognost import get_logger

logger = get_logger('amazonbot')


class AmazonBot(object):
	def __init__(self, isbn):
		self.isbn = isbn
		self.url_template = 'http://www.amazon.in/product-reviews/{isbn}/?showViewpoints=1&pageNumber={page_no}'
		self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}

	async def create_soup(self, page_no):
		"""
		Makes async request to the server and parses the
		responses using lxml tree builder

		:param page_no: int, which page to fetch
		:return: bs4.BeautifulSoup object
		"""
		url = self.url_template.format(isbn=self.isbn, page_no=page_no)
		response = await aiohttp.request('GET', url, headers=self.headers)
		html = await response.text()
		return BeautifulSoup(html, 'lxml')

	async def _num_review_pages(self):
		"""
		get the number of pages

		:return: tuple[int, bs4.BeautifulSoup]
		"""
		soup = await self.create_soup(1)
		pagination_bar = soup.find('div', attrs={'id': 'cm_cr-pagination_bar'})
		if pagination_bar:
			page_btn_li = pagination_bar.findAll('li', class_='page-button')
			return int(page_btn_li[-1].text.strip()), soup
		#: No pagination bar on the page doesn't imply
		#: that there are no reviews. It can also be due to
		#: the fact that the number of reviews were few enough
		#: to be accomodated on a single page only.
		#: if latter is the case, num_pages must be set to `1`.
		elif soup.find('div', attrs={'id': 'cm_cr-review_list'}):
			return 1, soup
		return 0, soup

	def build_review_dict(self, review):
		"""
		builds a single review

		:param review: review node containing a single review's metadata
		:return: dict
		"""
		review_dict = dict()
		review_dict['title'] = review.find('a', attrs={'data-hook': 'review-title'}).getText()
		review_dict['author'] = review.find('a', attrs={'data-hook': 'review-author'}).getText()
		review_dict['date'] = review.find('span', attrs={'data-hook': 'review-date'}).getText()[3:]
		review_dict['rating'] = review.find('i', attrs={'data-hook': 'review-star-rating'})['class'][2].split('-')[2]
		review_dict['body'] = review.find('span', attrs={'data-hook': 'review-body'}).getText()
		return review_dict

	def build_reviews_list(self, reviews_list_node):
		"""
		builds the list of all reviews available on a page

		:param reviews_list_node: node containing every review node on the page
		:return: list containing all the reviews available on current page
		"""
		reviews = []
		for review in reviews_list_node.children:
			if type(review) is Tag and review.get('data-hook') and review['data-hook'] == 'review':
				if review.get('class') and 'review' in review['class']:
					reviews.append(self.build_review_dict(review))
		return reviews

	async def get_reviews_from_page(self, page_no, soup=None):
		if not soup:
			soup = await self.create_soup(page_no)
		reviews_list_node = soup.find('div', attrs={'id': 'cm_cr-review_list'})
		return self.build_reviews_list(reviews_list_node)

	def get_reviews(self):
		"""
		Get reviews from all the pages,
		requests to all the pages are made
		concurrently, which decreases the overall
		time required to fetch all reviews

		:return: `list[dict]` which is json serializable
		"""
		reviews, tasks = [], []
		selector = selectors.SelectSelector()
		loop = asyncio.SelectorEventLoop(selector)
		asyncio.set_event_loop(loop)
		num_pages, soup = loop.run_until_complete(self._num_review_pages())
		for page in range(1, num_pages + 1):
			if page == 1:
				#: Reuse the response received on sending request
				#: to the first page to get total page count
				tasks.append(self.get_reviews_from_page(page, soup=soup))
			else:
				tasks.append(self.get_reviews_from_page(page))
		start = time.time()
		if tasks:
			waiting_tasks = asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
			completed_tasks, _ = loop.run_until_complete(waiting_tasks)
			loop.close()
			for task in completed_tasks:
				reviews.extend(task.result())
		logger.info('Fetched reviews from {p} page(s) in: {t} s'.format(t=time.time() - start, p=num_pages))
		return reviews
