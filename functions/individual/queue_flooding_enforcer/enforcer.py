from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import config
import time
import praw


class flooding:
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
		self.flooders = list()

		if config.frame == 'day':
			self.frame = 24*60*60
		elif config.frame == 'week':
			self.frame = 7*24*60*60


	# access modlog to acquire k flair names
	def modlog(self):
		now_time = time.time()
		for log in self.subreddit.mod.log(action='setsuggestedsort', mod='AutoModerator', limit=None):
			if now_time - log.created_utc  < self.frame:
				self.flooders.append(log.target_author)
			else:
				break


	# mainframe of k_flair_enforcer
	def main(self):
		self.modlog()
		unique_flood = list(set(self.flooders))

		print('Found ' + str(len(self.flooders)) + ' AutoModerator actions.')
		print('Removed ' + str(len(self.flooders)-len(unique_flood)) + ' duplicate users.')
		print('Left with ' + str(len(unique_flood)) + ' possible queue flooders.')


if __name__ == '__main__':
	flooding().main()
