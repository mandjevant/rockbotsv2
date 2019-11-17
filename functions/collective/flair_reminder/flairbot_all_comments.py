from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import threading
import config
import praw
import time


now_time = time.time()


class bot:
	# defined variables
	def __init__(self):
		self.sub = config.sub
		self.reddit = praw.Reddit(client_id = config.id, 
								  client_secret = config.secret, 
								  password = config.password, 
								  user_agent = config.user_agent, 
								  username = config.username)

		self.time_removal = config.time_removal
		self.time_flair = config.time_flair
																	
		self.flair_message =  config.flair_message
		self.removal_message = config.removal_message
		self.removal_title = config.removal_title
		self.removal_type = ('public')

		self.loggingdict = {}


	# takes submission ID to reply to in the form of a comment
	# returns the comment ID
	def comment(self, submission):
		sm = submission.reply(self.flair_message)
		sm.mod.distinguish(sticky=True)
		return sm.id


	# takes comment ID to remove the comment
	def comment_remove(self, comment):
		self.reddit.comment(comment).delete()							


	# takes submission ID to remove the submission
	def post_remove(self, submission):
		self.reddit.submission(submission).mod.remove()																						
		self.reddit.submission(submission).mod.send_removal_message(message = self.removal_message, title = self.removal_title, type = self.removal_type)	


	# takes submission ID to update loggingdict if submission is not yet present
	def add_to_dict(self, submission):
		if submission in self.loggingdict.keys():
			pass
		else:
			self.loggingdict.update({submission: [self.comment(submission), time.time()]})


	# checks submissions in new once/minute to see if flair has yet to be set
	def new_flair_check(self):	
		print('thread 1 running')	
		try: 												
			start_time = time.time()		

			while True:
				try:			
					for submission in self.reddit.subreddit(self.sub).new(limit=100): 
						if submission.link_flair_text == None and (time.time() - submission.created_utc) > self.time_flair and (time.time() - submission.created_utc) <= 600:
							self.add_to_dict(submission) 
						else:
							continue

					time.sleep(60.0 - ((time.time() - start_time) % 60.0))

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

		except KeyboardInterrupt:
			pass


	# checks submissions in loggingdict once/minute to see if flair is put
	# also handles exeptions 
	def responses_check(self):
		print('thread 2 running')
		try:
			start_time = time.time()		

			while True:																
				try: 												
					for key, value in self.loggingdict.copy().items():
						submission = self.reddit.submission(id=key)
						currentpostflair = submission.link_flair_text
						comment = value[0] #praw.models.Comment(reddit=self.reddit, id=value[0])
						post_time = value[1]

						if (((time.time() - post_time) >= self.time_removal) and ((time.time() - post_time) < self.time_removal + 300)):
							if currentpostflair == None:
								try:
									self.comment_remove(comment)
								except:
									print('comment already removed')
								try:
									self.post_remove(submission)
								except:
									print('post already removed')
								self.loggingdict.pop(submission)
							else:
								try:
									self.comment_remove(comment)
								except:
									print('comment already removed')
								self.loggingdict.pop(submission)

						elif (time.time() - post_time) < self.time_removal:
							if not(currentpostflair == None):
								try:
									self.comment_remove(comment)
								except:
									print('comment already removed')
								self.loggingdict.pop(submission)
							else:
								continue

					for key, value in self.loggingdict.items():
						if (time.time() - value[1]) > 7200:
							self.loggingdict.pop(key)

					time.sleep(60.0 - ((time.time() - start_time) % 60.0)) 	
							
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

		except KeyboardInterrupt:
			pass
		
	
	# checks new for nsfw flairs, marks nsfw accordingly
	def nsfwflair_check(self):
		print('thread 3 running')
		try: 												
			start_time = time.time()		

			while True:
				try:
					for submission in self.reddit.subreddit(self.sub).new(limit=100):
						if submission.link_flair_text != None:
							if submission.over_18 == False:
								flair = submission.link_flair_text
								if 'NSFW' in flair:
									submission.mod.nsfw()
								else:
									continue
							else:
								continue
						else: 
							continue

					time.sleep(60.0 - ((time.time() - start_time) % 60.0)) 	

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

		except KeyboardInterrupt:
			pass


	# threading to execute functions in parallel
	def threading(self):
		a = threading.Thread(target=self.new_flair_check, name='Thread-a', daemon=True)		
		b = threading.Thread(target=self.responses_check, name='Thread-b', daemon=True)		
		c = threading.Thread(target=self.nsfwflair_check, name='Thread-c', daemon=True)		

		a.start()																		
		b.start()																		
		c.start()																		

		a.join()																		
		b.join()
		c.join()																		


if __name__ == '__main__':
	bot().threading()

	print('Processing time:', time.time() - now_time)
