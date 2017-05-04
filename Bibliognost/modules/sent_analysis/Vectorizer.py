import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, BaseEstimator

lemmatizer = WordNetLemmatizer()


class LemmatizedTfidfVectorizer(TfidfVectorizer):
	def build_analyzer(self):
		"""
		Returns the Tfidf values on the lemmatized sequence of words obtained from the document string

		:return: function, that lemmatized the words extracted by the TfidfVectorizer's Word Analyser
		"""
		analyser = super(TfidfVectorizer, self).build_analyzer()
		return lambda doc: (lemmatizer.lemmatize(w) for w in analyser(doc))


class LinguisticVectorizer(BaseEstimator):
	# only transform method of BaseEstimator is defined
	def get_feature_names(self):
		"""
		Returns the features names for the vectorizer

		:return: np array containing the feature names
		"""
		return np.array(['nouns', 'adjectives', 'verbs', 'adverbs'])

	def fit(self, documents, y=None):
		return self

	def get_sentiments(self, d):
		"""
		Returns array of the float values for the respective features (noun, verb, adjective, adverb)

		:param d: String, document string is passed
		:return: array with the respective feature(noun, verb, adjective, adverb) extracted from the document string
		"""
		words = tuple(d.split())
		tagged = nltk.pos_tag(words)

		nouns = 0
		adjectives = 0
		verbs = 0
		adverbs = 0

		for word, pos_tag in tagged:

			if pos_tag.startswith("NN"):
				nouns += 1

			if pos_tag.startswith("JJ"):
				adjectives += 1

			if pos_tag.startswith("VB"):
				verbs += 1

			if pos_tag.startswith("RB"):
				adverbs += 1
		# adding one to consider empty document
		l = len(words) + 1
		return [nouns / l, adjectives / l, verbs / l, adverbs / l]

	def transform(self, documents):
		"""
		Returns np array of the feature vector obtained from the sets of document strings

		:param documents: np array of documents of dimension (M, 1), M = number of documents and each entry is a string
		:return: np array of sets of feature vector of dimension (M x N) where M is number of documents and N is the
				 features (here N = 4 as features are noun, verb, adjective, adverb)
		"""
		nouns, adjectives, verbs, adverbs = np.array([self.get_sentiments(d) for d in documents]).T
		result = np.array([nouns, adjectives, verbs, adverbs]).T
		return result
