import asyncio
import selectors
import time

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag

from Bibliognost import get_logger

logger = get_logger('amazonbot')

#: TO-DO - Mark all the pages which could not be fetched
#: due to any reason(remote server blocking our request to
#: prevent DDOS attack, network errors etc). When another
#: request comes with the same ISBN, try to fetch only those
#: pages which couldn't be fetched in the last request. Keep
#: doing this until all the reviews have been fetched.


class AmazonBot(object):
	def __init__(self, isbn):
		self.url_template = 'http://www.amazon.in/product-reviews/' + isbn + '/?showViewpoints=1&pageNumber={page_no}'
		self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}

	async def create_soup(self, session, page_no):
		"""
		Makes async request to the server and parses the
		responses using lxml tree builder

		:param session: aiohttp session object to fetch url
		:type session: aiohttp.client.ClientSession
		:param page_no: the webpage to fetch
		:type page_no: int
		:return: bs4.BeautifulSoup object
		"""
		url = self.url_template.format(page_no=page_no)
		async with session.get(url) as response:
			html = await response.text()
		return BeautifulSoup(html, 'lxml')

	async def _num_review_pages(self, session):
		"""
		get the number of pages

		:return: tuple[int, bs4.BeautifulSoup], total number of pages and soup object
		"""
		soup = await self.create_soup(session, 1)
		if soup:
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
		:type review: bs4.element.Tag
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
		:type reviews_list_node: bs4.element.Tag
		:return: list containing all the reviews available on current page
		"""
		reviews = []
		if reviews_list_node:
			for review in reviews_list_node.children:
				if type(review) is Tag and review.get('data-hook') and review['data-hook'] == 'review':
					if review.get('class') and 'review' in review['class']:
						reviews.append(self.build_review_dict(review))
		return reviews

	async def get_reviews_from_page(self, session, page_no, soup_obj=None):
		soup = soup_obj if soup_obj else await self.create_soup(session, page_no)
		reviews_list_node = soup.find('div', attrs={'id': 'cm_cr-review_list'})
		logger.info('Fetching page: {page}'.format(page=page_no))
		return self.build_reviews_list(reviews_list_node)

	def get_reviews(self):
		"""
		Get reviews from all the pages,
		requests to all the pages are made
		concurrently, which decreases the overall
		time required to fetch all reviews

		:return: `list[dict]` which is json serializable
		"""
		selector = selectors.SelectSelector()
		loop = asyncio.SelectorEventLoop(selector)
		asyncio.set_event_loop(loop)
		start = time.time()

		with aiohttp.ClientSession() as session:
			num_pages, soup = loop.run_until_complete(self._num_review_pages(session))
			pending_fetch_review_tasks = []
			for page in range(1, num_pages + 1):
				if soup and page == 1:
					pending_fetch_review_tasks.append(self.get_reviews_from_page(session, page, soup_obj=soup))
				else:
					pending_fetch_review_tasks.append(self.get_reviews_from_page(session, page))
			reviews = loop.run_until_complete(asyncio.gather(*pending_fetch_review_tasks, return_exceptions=True))
			loop.close()

		logger.info('Fetched reviews from {p} page(s) in: {t} s'.format(t=time.time() - start, p=num_pages))

		filtered_reviews = []
		for index, reviews_list in enumerate(reviews):
			if isinstance(reviews_list, Exception) or not reviews_list:
				cause = 'request blocked by remote server' if not reviews_list else reviews_list
				logger.warning('Failed to get result for page: {p}, cause={e}'.format(p=index + 1, e=cause))
			else:
				for review in reviews_list:
					filtered_reviews.append(review)
		return filtered_reviews
