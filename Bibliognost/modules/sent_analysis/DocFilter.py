import csv
import re

try:
	# positive
	# negative
	# unlabeled

	doc = set([])
	with open('C:/Users/tusha/Downloads/Compressed/processed_acl/books/negative.review', 'rb') as f:
		for inline in f:
			outline = ""
			inline = inline.decode('utf-8')
			pair = re.findall(r'(\(?[a-zA-Z0-9?!]*\)?_?\(?[a-zA-Z0-9?!]*\)?):\d+', inline)
			label = re.findall(r'#label#:(\w+)', inline)
			for wd in pair:
				word = re.findall(r'\(?[A-Za-z0-9?!]+\)?', wd)
				for w in word:
					if w[0] == '(':
						w[1:]
					if w[-1] == ')':
						w[:-1]
					outline = outline + w.lower().strip() + " "
			res = ""
			for wd in outline[:-1].split('!'):
				res = res + wd + " ! "
			final = ""
			for wd in res[:-3].split('?'):
				final = final + wd + " ? "
			outline = final[:-3]
			doc.add((outline, label[0].lower()))

	with open('C:/Users/tusha/Desktop/Bibliognost/SentimentAnalysis/Data/NegativeReview.csv', 'w', newline='') as csvf:
		writer = csv.writer(csvf, delimiter='\t')
		writer.writerow(['review', 'label'])
		writer.writerows(doc)

except Exception as e:
	print(e)
