from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import config
import praw
import time


class bot:
	# defining variables
	def __init__(self):
		self.reddit = praw.Reddit(
			client_id=config.id,
			client_secret=config.secret,
			password=config.password,
			user_agent=config.user_agent,
			username=config.username
		)

		self.subreddit = self.reddit.subreddit(config.sub)


	# assigns time of last flair edit to last_flair_utc
	def mod_log(self):
		a = False

		while a == False:
			try:
				for log in self.subreddit.mod.log(action="editflair", limit=100):
					if log.target_fullname != None:
						last_flair_utc = log.created_utc
						break

				a = True
				return last_flair_utc

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
				try:
					print(e.response.content)
				except:
					print(e)


	# assigns time of last comment to last_comment_utc
	def comment_hist(self):
		b = False

		while b == False:
			try:
				for comment in self.reddit.redditor(config.bot_username).comments.new(limit=1):
					last_comment_utc = comment.created_utc

				b = True
				return last_comment_utc

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
				try:
					print(e.response.content)
				except:
					print(e)


	# assigns time of last comment to lcu
	def cmc(self):
		c = False

		while c == False:
			try:
				n = 0
				for comment in self.reddit.redditor(config.bot_username_2).comments.new(limit=3):
					n+=1

					if n == 1:
						lcu = comment.created_utc
						first_title = comment.submission.title
					elif n == 2:
						second_title = comment.submission.title
					elif n == 3:
						third_title = comment.submission.title

				c = True
				if time.time() - lcu >= 300:
					if first_title == second_title and second_title == third_title:
						return True
					else:
						return False
				else:
					return False

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
				try:
					print(e.response.content)
				except:
					print(e)


	def main(self):
		log = self.mod_log()
		hist = self.comment_hist()
		cmc = self.cmc()

		return log, hist, cmc


if __name__ == '__main__':
	bot().main()
