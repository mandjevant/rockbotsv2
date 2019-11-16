from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import config
import praw


class elongate:
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


	# takes submission id, reports submission
	def report_sm(self, submission_id):
		try:
			self.reddit.submission(str(submission_id)).report('This submission is neither L O N G nor W I D E.')
		except Exception as e:
			try:
				print(e.response.content)
			except:
				print(e)


	# takes submission id, sets flair
	def flair(self, submission_id, ty):
		try:
			if ty == 'long':
				self.reddit.submission(str(submission_id)).flair.select(config.flair_id_long)
			elif ty == 'wide':
				self.reddit.submission(str(submission_id)).flair.select(config.flair_id_wide)
			else:
				pass
	
		except Exception as e:
			print(e)


	def main(self):
		while True:
			try:
				for sm in self.subreddit.stream.submissions(skip_existing=True):
					try:					
						if sm.selftext == '':
							h = vars(sm)['preview']['images'][0]['source']['height']
							w = vars(sm)['preview']['images'][0]['source']['width']

							if h > w:
								self.flair(sm.id, 'long')
							elif h < w:
								self.flair(sm.id, 'wide')
							elif h == w:
								self.report_sm(sm.id)
	
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
						try:
							self.report_sm(sm.id)
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


if __name__ == '__main__':
	elongate().main()
