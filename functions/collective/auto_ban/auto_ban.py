from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import threading
import config
import praw
import sys
import re


class flairer:
	# defining variables
	def __init__(self):
		self.reddit = praw.Reddit(client_id = config.id, 
								  client_secret = config.secret, 
								  password = config.password, 
								  user_agent = config.user_agent, 
								  username = config.username)

		self.subreddit = self.reddit.subreddit(str(config.sub))

		self.rules = dict()
		self.regexrules = dict()

		for key, value in config.rules.copy().items():
			if value[1] == True:
				self.regexrules.update({key: value[0]})
			elif value[1] == False:
				self.rules.update({key: value[0]})
			else:
				print('Rules contains unknown regex boolean.')
				sys.exit()


	###########################################################################
	# Section 1
	# This section contains user actions
	# Section 1.1; ban user
	# Section 1.2; mute user
	###########################################################################


	# bans a user
	def ban_user(self, item, word):
		try:
			self.subreddit.banned.add(item.author, ban_reason='You were banned from r/', config.sub, ' because your submission contained the word; ', word)
		except Exception as e:
			print(e.response.content)
			pass


	# mutes a user
	def mute_user(self, item):
		try:
			self.subreddit.muted.add(item.author, ban_reason='You were muted from r/', config.sub, '.')
		except Exception as e:
			print(e.response.content)
			pass


	###########################################################################
	# Section 2
	# This section contains item actions
	# Section 2.1; removing submission
	# Section 2.2; removing comment
	# Section 2.3; report submission
	# Section 2.4; report comment
	###########################################################################


	# removes submission
	def remove_submission(self, submission):
		try:
			self.reddit.submission(submission).mod.remove()
			#self.reddit.submission(submission).mod.send_removal_message()	
		except Exception as e:
			print(e.response.content)
			pass


	# removes comment
	def remove_comment(self, comment):
		try:
			self.reddit.comment(comment).mod.remove()
			#self.reddit.comment(comment).mod.send_removal_message()
		except Exception as e:
			print(e.response.content)
			pass


	# reports submission
	def report_submission(self, submission, word):
		try:
			self.reddit.submission(submission).report('Please review this submission. It contains the word; ' + word)
		except Exception as e:
			print(e.response.content)
			pass


	# reports comment
	def report_comment(self, comment, word):
		try:
			self.reddit.comment(comment).report('Please review this comment. It contains the word; ' + word)
		except Exception as e:
			print(e.response.content)
			pass


	###########################################################################
	# Section 3
	# This section contains item checks
	# Section 3.1; checks submission body
	# Section 3.2; checks submission title
	# Section 3.3; checks comment 
	###########################################################################


	# gets body of submission
	def sub_body(self, submission):
		body = self.reddit.submission(submission).selftext
		self.check_for(submission, body, itemtype='submission')
		self.check_regex(submission, body, itemtype='submission')


	# gets title of submission
	def sub_title(self, submission):
		title = self.reddit.submission(submission).title
		self.check_for(submission, title, itemtype='submission')
		self.check_regex(submission, title, itemtype='submission')


	# gets comment body
	def comment_body(self, comment):
		body = self.reddit.comment(comment).body
		self.check_for(comment, body, itemtype='comment')
		self.check_regex(comment, body, itemtype='comment')
		

	###########################################################################
	# Section 4
	# This section checks if text contains a word and acts
	# Section 4.1; acts on the item if it contains word
	# Section 4.2; checks text for word
	# Section 4.3; checks text for regex
	###########################################################################


	# acts on the item based on the value
	def act(self, item, key, value, itemtype):
		if value == 'ban':
			self.ban_user(item, key)
		elif value == 'mute':
			self.mute_user(item)
		elif value == 'remove':
			if itemtype == 'submission':
				self.remove_submission(item)
			else:
				self.remove_comment(item)
		elif value == 'report':
			if itemtype == 'submission':
				self.report_submission(item, key)
			else:
				self.report_comment(item, key)
		else:
			print('Rules contains unknown action.')
			sys.exit()
	

	# checks if text contains words from self.rules
	def check_for(self, item, words, itemtype):
		for key, value in self.rules.items():
			if key in words:
				self.act(item, key, value, itemtype)
			else:
				continue


	# checks if text contains regex
	def check_regex(self, item, words, itemtype):
		for key, value in self.regexrules.items():
			if re.search(key, words):
				self.act(item, key, value, itemtype)
			else:
				continue


	###########################################################################
	# Section 5
	# This section checks submission and comment streams
	# Section 5.1; checks submission stream
	# Section 5.2; checks comment stream
	# Section 5.3; uses threading to check stream in parallel
	###########################################################################


	# checks submissions stream
	def check_submissions(self):
		while True:
			try:
				for submission in self.subreddit.stream.submissions():
					self.sub_body(submission)
					self.sub_title(submission)
					
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


	# checks new comments
	def check_comments(self):
		while True:
			try:
				for comment in self.subreddit.stream.comments():
					self.comment_body(comment)

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


	# threading to start streams in parallel
	def threading(self):
		if config.checking == 'all':
			a = threading.Thread(target=self.check_submissions, name='Thread-a', daemon=True)
			b = threading.Thread(target=self.check_comments, name='Thread-b', daemon=True)

			a.start()
			b.start()

			a.join()
			b.join()

		elif config.checking == 'submissions':
			self.check_submissions()
		elif config.checking == 'comments':
			self.check_comments()
		else:
			print('Config includes uknown parameter.')
			sys.exit()


if __name__ == '__main__':
	flairer().threading()
