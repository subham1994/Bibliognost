import xml.etree.ElementTree as elTree
from urllib import parse

import requests

from . import grresponse
from Bibliognost import credentials


class BookSearch:
	def __init__(self, book_title):
		self.url = 'https://www.goodreads.com/search/index?{query_params}'
		self.query_params = parse.urlencode({'key': credentials['goodreads']['key'], 'q': book_title, 'format': 'xml'})
		self.response = requests.get(self.url.format(query_params=self.query_params))
		self.root = elTree.fromstring(self.response.content)
		self.search_node = self.root.find(grresponse.SEARCH_NODE_TAG)

	def get_results(self):
		search_results = []
		result_node = self.search_node.find(grresponse.RESULT_NODE_TAG)
		for node in result_node.findall(grresponse.WORK_NODE_TAG):
			best_book_node = node.find(grresponse.BEST_BOOK_NODE_TAG)
			result_dict = {}
			if best_book_node:
				for child in grresponse.BEST_BOOK_NODE_DESCENDENTS:
					result_dict[child] = best_book_node.find(child).text
				search_results.append(result_dict)
		return search_results
