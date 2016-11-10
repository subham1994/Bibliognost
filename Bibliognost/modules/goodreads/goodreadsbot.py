import asyncio
import selectors
import time

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag

from Bibliognost import get_logger

logger = get_logger('amazonbot')


class GoodReadsBot(object):
	def __init__(self, url):
		self.url_template = url
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

	async def _fetch_dynamically_loaded_pages(self):
		pass

	async def _get_review_pages_count(self):
		pass

	def build_review_dict(self):
		pass

	def build_reviews_list(self):
		pass

	async def get_reviews_from_page(self):
		pass

	def get_reviews(self):
		with aiohttp.ClientSession() as session:

