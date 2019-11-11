from prawcore.exceptions import RequestException, ResponseException, InvalidToken
from nltk.cluster.util import cosine_distance
from nltk.corpus import stopwords
from nltk import tokenize
import networkx as nx
import wikipediaapi
import numpy as np
import config
import praw
import time
import re


class WhothisBot:
	# defining variables
	def __init__(self):
		self.reddit = praw.Reddit(
			client_id=config.id,
			client_secret=config.secret,
			password=config.password,
			user_agent=config.user_agent,
			username=config.username
		)

		self.subreddit = self.reddit.subreddit(str(config.sub))


	# parse comment
	def parse_comment(self, comment):
		try: 
			# separate comment by "!whothis "
			splitted = comment.split("!whothis ")
			# filter out emplty spaces and faulty values
			splitted = list(filter(None, splitted))
			# if there is something after !whothis
			if len(splitted) > 0:
				# return the comment part after !whothis
				return splitted[len(splitted)-1]
			else:
				# otherwise return empty string
				return ""
		
		except Exception as e:
			print(e)


	# gets wikipedia summary
	def get_wiki_summary(self, query):
		try:
			wiki = wikipediaapi.Wikipedia('en')
			wiki_page = wiki.page(query)
			if wiki_page.exists():
				return wiki_page.summary, wiki_page.fullurl
			else:
				return 'Whothis bot could not find any information about your query ' + str(query) + '. Sorry! :('
			
		except Exception as e:
			print(e)


	# takes 2 sentences and stop words
	# returns similarity of sentence 
	def sentence_similarity(self, sent1, sent2, stopwords=None):
		if stopwords == None:
			stopwords = []

		sent1 = [w.lower() for w in sent1]
		sent2 = [w.lower() for w in sent2]
	
		all_words = list(set(sent1 + sent2))
	
		vector1 = [0] * len(all_words)
		vector2 = [0] * len(all_words)
	
		# build the vector for the first sentence
		for w in sent1:
			if w in stopwords:
				continue
			vector1[all_words.index(w)] += 1
	
		# build the vector for the second sentence
		for w in sent2:
			if w in stopwords:
				continue
			vector2[all_words.index(w)] += 1
	
		return 1 - cosine_distance(vector1, vector2)


	# takes list of sentences and stop words
	# creates similarity matrix based on cosine distance
	def build_similarity_matrix(self, sentences, stop_words):
		# Create an empty similarity matrix
		similarity_matrix = np.zeros((len(sentences), len(sentences)))
	
		for idx1 in range(len(sentences)):
			for idx2 in range(len(sentences)):
				if idx1 == idx2: #ignore if both are same sentences
					continue 
				similarity_matrix[idx1][idx2] = self.sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

		return similarity_matrix


	# summarization main
	def summarize(self, wiki, len_sen):
		sentences = tokenize.sent_tokenize(wiki)
		stop_words = stopwords.words('english')
		summarize_text = list()
		
		sentence_similarity_matrix = self.build_similarity_matrix(sentences, stop_words)
		scores = nx.pagerank(nx.from_numpy_matrix(sentence_similarity_matrix))

		ranked_sent = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)

		for i in range(len_sen):
			summarize_text.append("".join(ranked_sent[i][1]))

		return summarize_text


	# responds to comment
	def printcomments(self):
		try:
			for comment in self.subreddit.stream.comments(skip_existing=True):
				try:
					if '!whothis ' in comment.body:
						whothis = self.parse_comment(comment.body)
						if re.search('(?<=\s)h\s*e\s*l\s*p', whothis) != None:
							comment.reply(config.helpmsg)
						else: 
							wiki_summary, wiki_url = self.get_wiki_summary(whothis)

							# # Bad way of summarizing
							# sentences = tokenize.sent_tokenize(wiki_summary)
							# if len(sentences) > 5:
							# 	sentences = sentences[:5]

							# wiki_summary = ""
							# for i in range(len(sentences)):
							# 	wiki_summary = wiki_summary + i

							# Good way of summarizing
							sentences = tokenize.sent_tokenize(wiki_summary)
							if len(sentences) > 5:
								summ = self.summarize(wiki_summary, 5)

							wiki_summary = ""
							for i in summ:
								wiki_summary = wiki_summary + " " + i

							print("retrieving information about " + str(whothis))
							comment.reply(wiki_summary + "\n\n *[source](" + wiki_url + ")*")

				except InvalidToken:
					print("Encountered Invalid Token error, resetting PRAW")
					time.sleep(10)
					self.reddit = None
					self.reddit = praw.Reddit(username = config.username,
										  password = config.password,
										  client_id = config.id,
										  client_secret = config.secret,
										  user_agent = config.user_agent)
					self.subreddit = self.reddit.subreddit(str(config.sub))
						
				except RequestException as e:
					print(e)
					print("Request problem, will retry\n")
					time.sleep(10)
					
				except ResponseException as e:
					print(e)
					print("Server problem, will retry\n")
					time.sleep(60)
					
				except Exception as e:
					print(e)

		except InvalidToken:
			print("Encountered Invalid Token error, resetting PRAW")
			time.sleep(10)
			self.reddit = None
			self.reddit = praw.Reddit(username = config.username,
								  password = config.password,
								  client_id = config.id,
								  client_secret = config.secret,
								  user_agent = config.user_agent)
			self.subreddit = self.reddit.subreddit(str(config.sub))
				
		except RequestException as e:
			print(e)
			print("Request problem, will retry\n")
			time.sleep(10)
			
		except ResponseException as e:
			print(e)
			print("Server problem, will retry\n")
			time.sleep(60)
			
		except Exception as e:
			print(e)


if __name__ == "__main__":
	WhothisBot().printcomments()
	