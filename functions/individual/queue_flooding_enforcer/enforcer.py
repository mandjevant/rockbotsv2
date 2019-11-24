from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import config
import time
import praw


class flooders:
	# defining variables
	def __init__(self):
		self.reddit = praw.Reddit(
			client_id=config.id,
			client_secret=config.secret,
			password=config.password,
			user_agent=config.user_agent,
			username=config.username
		)

		self.check_subreddit = self.reddit.subreddit(str(config.checking_sub))
		self.flooded_subreddit = self.reddit.subreddit(str(config.flooder_sub))
		self.flooders = list()
		self.mod_team = [x for x in self.check_subreddit.moderator()]


	# access modlog to acquire k flair names
	def modlog(self, frame):
		flooders = list()
		now_time = time.time()

		for log in self.flooded_subreddit.mod.log(action='setsuggestedsort', mod='AutoModerator', limit=None):
			if now_time - log.created_utc  < frame:
				flooders.append(log.target_author)
			else:
				break

		return flooders


	# parses comment body for time frame
	def time_frame_parser(self, body):
		if body[:3] == 'day':
			frame = 24*60*60
		elif body[:6] == '2 days':
			frame = 2*24*60*60
		elif body[:5] == '2days':
			frame = 2*24*60*60
		elif body[:6] == '3 days':
			frame = 3*24*60*60
		elif body[:5] == '3days':
			frame = 3*24*60*60
		elif body[:6] == '4 days':
			frame = 4*24*60*60
		elif body[:5] == '4days':
			frame = 4*24*60*60
		elif body[:6] == '5 days':
			frame = 5*24*60*60
		elif body[:5] == '5days':
			frame = 5*24*60*60
		elif body[:6] == '6 days':
			frame = 6*24*60*60
		elif body[:5] == '6days':
			frame = 6*24*60*60
		elif body[:4] == 'week':
			frame = 7*24*60*60
		elif body[:7] == '2 weeks':
			frame = 2*7*24*60*60
		elif body[:6] == '2weeks':
			frame = 2*7*24*60*60
		elif body[:7] == '3 weeks':
			frame = 3*7*24*60*60
		elif body[:6] == '3weeks':
			frame = 3*7*24*60*60
		elif body[:5] == 'month':
			frame = 4*7*24*60*60
		elif body[:7] == '6 weeks':
			frame = 6*7*24*60*60
		elif body[:6] == '6weeks':
			frame = 6*7*24*60*60
		elif body[:8] == '2 months':
			frame = 8*7*24*60*60
		elif body[:7] == '2months':
			frame = 8*7*24*60*60

		return frame


	# takes comment id replies to comment
	def comment_reply(self, comment, message):
		try:
			cm = comment.reply(message)
		except Exception as e:
			print(e)
			pass


	def flooder_user_data(self, username, frame):
		perday, total, five, ten, fifteen, twenty = 0, 0, 0, 0, 0, 0
		perdaytimer = time.time()

		try:
			for submission in self.reddit.redditor(username).submissions.new(limit=None):
				try:
					if time.time() - submission.created_utc <= frame:
						if submission.subreddit.display_name == config.flooder_sub:
							total+=1

							if submission.created_utc > perdaytimer-24*60*60:
								perday+=1
							else:
								perdaytimer = submission.created_utc
								
								if perday > 5 and perday <= 10:
									five+=1
								elif perday > 10 and perday <= 15:
									ten+=1
								elif perday > 15 and perday <= 20:
									fifteen+=1
								elif perday > 20:
									twenty+=1

								perday=1
						else:
							pass
					else:
						if perday > 5 and perday <= 10:
							five+=1
						elif perday > 10 and perday <= 15:
							ten+=1
						elif perday > 15 and perday <= 20:
							fifteen+=1
						elif perday > 20:
							twenty+=1
						break
				
				except Exception as e:
					print(e)
					pass

		except InvalidToken:
			print("Encountered Invalid Token error, resetting PRAW")
			time.sleep(10)
			self.reddit = None
			self.reddit = praw.Reddit(username = config.username,
								  password = config.password,
								  client_id = config.id,
								  client_secret = config.secret,
							  	  user_agent = config.user_agent)
			
			self.check_subreddit = self.reddit.subreddit(str(config.checking_sub))
			self.flooded_subreddit = self.reddit.subreddit(str(config.flooder_sub))
				
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

		return total, five, ten, fifteen, twenty


	# mainframe of k_flair_enforcer
	def flooders_main(self, comment, body):
		self.start_time = time.time()
		frame = self.time_frame_parser(body)

		flooders = self.modlog(frame)
		unique_flood = list(set(flooders))

		msg = '* Found ' + str(len(flooders)) + ' AutoModerator actions. \n' + '* Removed ' + str(len(flooders)-len(unique_flood)) + ' duplicate users. \n' + '* Left with ' + str(len(unique_flood)) + ' possible queue flooders. \n\n # Flooders \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg2 = '# Flooders part 2 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg3 = '# Flooders part 3 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg4 = '# Flooders part 4 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg5 = '# Flooders part 5 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg6 = '# Flooders part 6 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg7 = '# Flooders part 7 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg8 = '# Flooders part 8 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg9 = '# Flooders part 9 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'
		msg10 = '# Flooders part 10 \n\n| User | No. submissions in timeframe | No. days 5+ | No. days 10+ | No. days 15+ | No. days 20+ |\n| --- | --- | --- | --- | --- | --- |'

		for user in unique_flood:
			total, five, ten, fifteen, twenty = self.flooder_user_data(user, frame)
			if len(msg) > 9500:
				if len(msg2) > 9500:
					if len(msg3) > 9500:
						if len(msg4) > 9500:
							if len(msg5) > 9500:
								if len(msg6) > 9500:
									if len(msg7) > 9500:
										if len(msg8) > 9500:
											if len(msg8) > 9500:
												if len(msg10) > 9500:
													msg10 = msg10 + "\n\n Wayyyy too many people to display so I stopped"
													break
												else:
													msg10 = msg10 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
											else:
												msg9 = msg9 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
										else:
											msg8 = msg8 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
									else:
										msg7 = msg7 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
								else:
									msg6 = msg6 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
							else:
								msg5 = msg5 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
						else:
							msg4 = msg4 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
					else:
						msg3 = msg3 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
				else:
					msg2 = msg2 + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)
			else:
				msg = msg + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(user, total, five, ten, fifteen, twenty)

		self.comment_reply(comment, 'Well, it took me ' + str(round(time.time()-self.start_time,2)) + ' seconds, but: \n' + msg)

		if len(msg2) > 0:
			self.comment_reply(comment, msg2)
		elif len(msg3) > 0:
			self.comment_reply(comment, msg3)
		elif len(msg4) > 0:
			self.comment_reply(comment, msg4)
		elif len(msg5) > 0:
			self.comment_reply(comment, msg5)
		elif len(msg6) > 0:
			self.comment_reply(comment, msg6)
		elif len(msg7) > 0:
			self.comment_reply(comment, msg7)
		elif len(msg8) > 0:
			self.comment_reply(comment, msg8)
		elif len(msg9) > 0:
			self.comment_reply(comment, msg9)
		elif len(msg10) > 0:
			self.comment_reply(comment, msg10)


	# checks comment stream
	# mainframe for commands when detected
	def commands(self):
		while True:
			try:
				for comment in self.check_subreddit.stream.comments(skip_existing=True):
					try:
						if comment.author.name in self.mod_team:
							if comment.body[:9] == '!flooders':
								self.flooders_main(comment, comment.body[10:])
							elif comment.body[:10] == '!floodersp':
								self.flood_person_main(comment, comment.body[11:])
							elif comment.body[:16] == '!flooders person':
								self.flood_person_main(comment, comment.body[17:])
						else:
							pass

					except Exception as e:
						print(e)
						pass

			except InvalidToken:
				print("Encountered Invalid Token error, resetting PRAW")
				time.sleep(10)
				self.reddit = None
				self.reddit = praw.Reddit(username = config.username,
									  password = config.password,
									  client_id = config.id,
									  client_secret = config.secret,
								  	  user_agent = config.user_agent)
				
				self.check_subreddit = self.reddit.subreddit(str(config.checking_sub))
				self.flooded_subreddit = self.reddit.subreddit(str(config.flooder_sub))
					
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
	flooders().commands()
