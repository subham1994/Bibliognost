import csv
import os
import pickle
import time

import numpy as np
from sklearn.metrics import f1_score
from sklearn.model_selection import ShuffleSplit
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion

from . import PathInfo
from .Vectorizer import LinguisticVectorizer, LemmatizedTfidfVectorizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data(dirname=PathInfo.DATA_BASE_DIR, file=PathInfo.MIXED_REVIEW_FILE):
	"""
	Loads data from file and converts it into X, Y pairs w

	:param dirname: `str`, the name of directory
	:param file: takes any one of intially processed review file (positive, negative and mixed)
	:return: tuple, Data set in form of X, Y where both X and Y are np array
	"""
	data = []
	# reading datasets from the file
	path = os.path.join(BASE_DIR, '{dir}{file}'.format(dir=dirname, file=file))
	with open(path, 'r', newline='') as f:
		csvreader = csv.reader(f, delimiter='\t')
		next(csvreader)
		for line in csvreader:
			x = line[0]
			if line[1].lower() == 'positive':
				y = 1
			else:
				y = 0
			data.append([x, y])
	X = np.asarray([d[0] for d in data], dtype=object)
	Y = np.asarray([d[1] for d in data], dtype='u1')
	return X, Y


def all_feature_vectorizer():
	"""
	Combines the linguistic vectorizer and lemmatized TfidfVectorizer

	:return: Vectorizer class, which is combination of the above two vectorizer in respective order
	"""
	linguistic_vectorizer = LinguisticVectorizer()
	lemm_tf_idf_vect = LemmatizedTfidfVectorizer(
		analyzer='word', ngram_range=(1, 2), min_df=2, use_idf=True,
		smooth_idf=True, stop_words=None, sublinear_tf=True, binary=False
	)
	# Feature union acts as pipeline that combines the features from the individual Vectorizer
	all_features = FeatureUnion([('lingVec', linguistic_vectorizer), ('lemmaVec', lemm_tf_idf_vect)])
	return all_features


def train_model(clf_generator, X, Y, dev=False):
	"""
	Trains the classifier and return the best classifer based on the F1 Score

	:param clf_generator: Class of data classifier (here : MultinomailNB)
	:param X: np array of the feature vector with dimension (M, N), where M is number of entries and N is feature vector
	:param Y: np array of result vector with dimension (M x 1), where M is number of entries and entries are binary(0/1)
	:param dev: boolean , for displaying statistic of each itreation within the training loop
	:return: object, the best classifier's object based on the F1-Score
	"""
	score, f1score = [], []
	# best classifier variable
	bestclf = clf_generator()
	# max f1score
	maxf1score = 0
	# test score for the max f1score
	selectedtestscore = 0

	rs = ShuffleSplit(n_splits=15, test_size=0.25, train_size=None, random_state=0)
	# training loop
	for train_index, test_index in rs.split(X):
		# training set
		X_train, Y_train = X[train_index], Y[train_index]
		# test set
		X_test, Y_test = X[test_index], Y[test_index]

		clf = clf_generator(alpha=0.1)
		clf.fit(X_train, Y_train)
		testscore = clf.score(X_test, Y_test)
		testresult = clf.predict(X_test)
		testf1score = f1_score(Y_test, testresult)
		if dev:
			print('>>testscore : ', testscore, 'f1-score: ', testf1score)
		if testf1score > maxf1score:
			maxf1score = testf1score
			selectedtestscore = testscore
			bestclf = clf
		score.append(testscore)
		f1score.append(testf1score)
	print('-' * 80)
	print("Overall | Avg_acc: %.3f\tStd_dev: %.3f\tAvg_f1score: %.3f\tStd_dev: %.3f" % (
		np.mean(score), np.std(score), np.mean(f1score), np.std(f1score)))
	print("Selected Classifier | Acc: %.3f\tF1score: %.3f" % (selectedtestscore, maxf1score))
	print('-' * 80)
	return bestclf


def predict_sentiment(review):
	"""
	Returns the sentiment of the document string (positive or negative)

	:param review: string, document string is passed as an argument
	:return: binary value 0 for negative and 1 for positive
	"""

	# statistics :
	# Best Multinomail Classifier with allFeature Vectorizer gives the following output for negative(only) data sets and
	# positive(only) data sets.
	# neg : 0.747663551402  #pos : 0.909365558912

	print("Extracting the Features from the input.")
	start = time.time()
	X_test = vectorizer.transform(review)
	print("Feature Extraction done in  %.3f secs" % (time.time() - start))

	print("Sentiment classification of the the input.")
	start = time.time()
	sentiment = clf.predict(X_test)
	print("Classification done in  %.3f secs" % (time.time() - start))
	return sentiment


if os.path.isfile(os.path.join(BASE_DIR, PathInfo.PICKLE_BASE_DIR + PathInfo.INIT_CLASSIFIER)):
	print("Loading the vectorizer")
	start = time.time()
	with open(os.path.join(BASE_DIR, PathInfo.PICKLE_BASE_DIR + PathInfo.INIT_VECTORIZER), 'rb') as vect_f:
		vectorizer = pickle.load(vect_f)
	print("Vectorizer loaded in  %.3f" % (time.time() - start))

	print("Loading the classifier.")
	start = time.time()
	with open(os.path.join(BASE_DIR, PathInfo.PICKLE_BASE_DIR + PathInfo.INIT_CLASSIFIER), 'rb') as clf_f:
		clf = pickle.load(clf_f)
	print("Classifier loaded in  %.3f" % (time.time() - start))

else:
	print("Loading the data sets.")
	start = time.time()
	X, Y = load_data(file=PathInfo.MIXED_REVIEW_FILE)
	print("Data sets loaded in %.2f secs." % (time.time() - start))

	print("Extracting the features.")
	vectorizer = all_feature_vectorizer()
	start = time.time()
	X_Features = vectorizer.fit_transform(X)
	print("Feature Extraction done in %.3f" % (time.time() - start))

	with open(os.path.join(BASE_DIR, PathInfo.PICKLE_BASE_DIR + PathInfo.INIT_VECTORIZER), 'wb') as vect_f:
		pickle.dump(vectorizer, vect_f)

	print("Training the classifier.")
	start = time.time()
	clf = train_model(MultinomialNB, X_Features, Y)
	print("Classifier trained in %.3f secs." % (time.time() - start))

	with open(os.path.join(BASE_DIR, PathInfo.PICKLE_BASE_DIR + PathInfo.INIT_CLASSIFIER), 'wb') as clf_f:
		pickle.dump(clf, clf_f)
