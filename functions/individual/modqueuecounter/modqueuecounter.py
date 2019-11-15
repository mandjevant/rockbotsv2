from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import praw
import time


class bot:
	# defined variables
	def __init__(self):
		self.sub = input('What subreddit to check? `mod` regards all subs. ') 
		self.oauth = input('What is your oauth code? If 2fa is disabled, respond `None`.')
		if 'None' in oauth:
			self.reddit = praw.Reddit(client_id = config.id, 
									  client_secret = config.secret, 
									  password = config.password, 
									  user_agent = config.user_agent, 
									  username = config.username)
		else:
			self.password = config.password+':'+self.oauth
			self.reddit = praw.Reddit(client_id = config.id, 
									  client_secret = config.secret, 
									  password = self.password, 
									  user_agent = config.user_agent, 
									  username = config.username)


	# number of posts in modqueue
	def count(self):
		n = 0
		for item in self.reddit.subreddit(self.sub).mod.modqueue(limit=None):
			n = n + 1

		return str(n)


	def main(self):
		t = False
		while t == False:
			try:
				print('Total items in queue for r/' + self.sub + ' = ' + self.count())
				t = True

			except InvalidToken:
				print("Encountered Invalid Token error, resetting PRAW")
				time.sleep(10)
				self.sub = input('What subreddit to check? `mod` regards all subs. ') 
				self.oauth = input('What is your oauth code? If 2fa is disabled, respond `None`.')
				if 'None' in oauth:
					self.reddit = praw.Reddit(client_id = config.id, 
											  client_secret = config.secret, 
											  password = config.password, 
											  user_agent = config.user_agent, 
											  username = config.username)
				else:
					self.password = config.password+':'+self.oauth
					self.reddit = praw.Reddit(client_id = config.id, 
											  client_secret = config.secret, 
											  password = self.password, 
											  user_agent = config.user_agent, 
											  username = config.username)
					
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
	bot().main()
	