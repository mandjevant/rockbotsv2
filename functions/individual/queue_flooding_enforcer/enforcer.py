from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import calendar
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
		now_time = time.time()
		done4 =  False

		while done4 == False:
			flooders = list()

			try:
				for log in self.flooded_subreddit.mod.log(action='setsuggestedsort', mod='AutoModerator', limit=None):
					if now_time - log.created_utc  < frame:
						flooders.append(log.target_author)
					else:
						break

				done4 = True

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


	# retrieves usernotes wiki
	def retrieve(self):
		wikipage = self.flooded_subreddit.wiki['usernotes']
		content = wikipage.content_md
		full_d = json.loads(content.replace("'", "\""))
		blob = full_d['blob']

		return blob, full_d
		

	# decodes and decompresses
	def translate(self, blob):
		decoded = base64.b64decode(blob)
		decompressed = zlib.decompress(decoded)

		return decompressed


	# encodes and compresses
	def encode(self, blob):
		blob = json.dumps(blob).encode('utf-8')
		compressed_blob = zlib.compress(blob)
		encoded_blob = base64.b64encode(compressed_blob)

		return encoded_blob


	# replaces old and new wiki text
	def replace(self, text):
		self.flooded_subreddit.wiki['usernotes'].edit(content=text,reason="Queueflooder")


	# main program
	def usernote(self, user, usernote):
		blob, full_d = self.retrieve()
		d_blob = self.translate(blob)
		loaded_d_blob = json.loads(d_blob)

		if config.username not in full_d["constants"]["users"]:
			full_d["constants"]["users"] += [config.username]

		if "spamwatch" not in full_d["constants"]["warnings"]:
			full_d["constants"]["warnings"] += ["spamwatch"]

		if user in list(loaded_d_blob.keys()):
			loaded_d_blob[user]["ns"].insert(0, {"n":usernote,"t":int(round(time.time(),0)),"m":full_d["constants"]["users"].index(config.username),"l":"","w":full_d["constants"]["warnings"].index("spamwatch")})
		else:
			loaded_d_blob.update({user:{"ns":[{"n":usernote,"t":int(round(time.time(),0)),"m":full_d["constants"]["users"].index(config.username),"l":"","w":full_d["constants"]["warnings"].index("spamwatch")}]}})

		full_d["blob"] = self.encode(loaded_d_blob).decode("utf-8")
		full_d = json.dumps(full_d)

		self.replace(full_d)


	# takes comment id replies to comment
	def comment_reply(self, comment, message):
		try:
			cm = comment.reply(message)
		except Exception as e:
			print(e)
			pass


	# main flooders user data
	def flooders_user_data(self, username, frame):
		perday, total, five, ten, fifteen, twenty = 0, 0, 0, 0, 0, 0
		perdaytimer = time.time()
		done3 = False

		while done3 == False:
			try:
				for submission in self.reddit.redditor(username).submissions.new(limit=None):
					try:
						if time.time() - submission.created_utc <= frame:
							if submission.subreddit.display_name == config.flooder_sub:
								total+=1

								if submission.created_utc >= perdaytimer-24*60*60:
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

				done3 = True

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
			total, five, ten, fifteen, twenty = self.flooders_user_data(user, frame)
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

		if len(msg2) > 160:
			self.comment_reply(comment, msg2)
		elif len(msg3) > 160:
			self.comment_reply(comment, msg3)
		elif len(msg4) > 160:
			self.comment_reply(comment, msg4)
		elif len(msg5) > 160:
			self.comment_reply(comment, msg5)
		elif len(msg6) > 160:
			self.comment_reply(comment, msg6)
		elif len(msg7) > 160:
			self.comment_reply(comment, msg7)
		elif len(msg8) > 160:
			self.comment_reply(comment, msg8)
		elif len(msg9) > 160:
			self.comment_reply(comment, msg9)
		elif len(msg10) > 160:
			self.comment_reply(comment, msg10)


	# parses comment for individual data presentation
	def person_parser(self, body):
		index = body.find(' ')
		username = body[:index].replace('\\', '')
		timeframe = self.time_frame_parser(body[index+1:])

		return username, timeframe


	# acquire data for user table
	def user_table(self, username, frame):
		totalu = 0
		totaltotalu = 0
		done = False

		while done == False:
			try:
				for submission in self.reddit.redditor(username).submissions.new(limit=None):
					try:
						if submission.subreddit.display_name == config.flooder_sub:
							totaltotalu+=1
							
							if time.time() - submission.created_utc <= frame:
								totalu+=1

							else:
								pass
						else:
							pass
					
					except Exception as e:
						print(e)
						pass
				
				karma = self.reddit.redditor(username).link_karma + self.reddit.redditor(username).comment_karma
				age = str(time.strftime("%x %X", time.gmtime(self.reddit.redditor(username).created_utc)))
				banned = str(any(self.flooded_subreddit.banned(redditor=username)))

				done = True

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

		return totaltotalu, totalu, karma, age, banned


	# returns individual user data 
	def submission_table(self, username, frame):
		done2 = False
		umsg = "\n\n# General user data \n\n| User | Submission in sub | Submission in timeframe | User karma | User age | User banned |\n| --- | --- | --- | --- | --- | --- |"
		totaltotalu, totalu, karma, age, banned = self.user_table(username, frame)

		umsg = umsg + "\n| [{0}](https://www.reddit.com/user/{0}) | {1} | {2} | {3} | {4} | {5} |".format(username, str(totaltotalu), str(totalu), karma, age, banned)
		umsg = umsg + "\n\n# User submissions \n\n| Submission | Score | Reports | Removed | Created |\n| --- | --- | --- | --- | --- |"

		while done2 == False:
			try:
				for submission in self.reddit.redditor(username).submissions.new(limit=None):
					try:
						if time.time() - submission.created_utc <= frame:
							if submission.subreddit.display_name == config.flooder_sub:
								if submission.banned_by == None or submission.banned_by == 'None':
									removed = False
								else:
									removed = True

								umsg = umsg + "\n| [{0}]({1})[.]({6}) | {2} | {3} | {4} | {5} |".format(submission.title, submission.permalink, str(submission.score), str(submission.num_reports), str(removed), str(time.strftime("%x %X", time.gmtime(submission.created_utc))), submission.url)

							else:
								pass
						else:
							# break parsing
							break
					
					except Exception as e:
						print(e)
						pass

				done2 = True

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

		return umsg


	# mainframe for user display
	def flood_person_main(self, comment, body):
		username, timeframe = self.person_parser(body)
		umsg = self.submission_table(username, timeframe)
		self.comment_reply(comment, umsg)


	# takes user and time 
	# bans user for said time
	def ban_user(self, user, time):
		try:
			self.flooded_subreddit.banned.add(user, duration=time, note='Queue flooding ' + str(time) + ' days.', ban_message="You've been banned for queue flooding. The limit is 5 POSTS PER DAY. Exceeding this limit has resulted in your temporary ban. If you feel the need to spam your memes, please proceed to post them at r/modsgay.")
		except Exception as e:
			print(e)
			pass


	# removes k flair from user
	def remove_k_flair(username):
		for i in self.subreddit.flair(redditor=self.reddit.redditor(username)):
			css_class = i['flair_css_class']
			text = i['flair_text']

		if css_class == 'k':
			self.subreddit.flair.set(redditor=self.reddit.redditor(username),text=text,css_class="")


	# mainframe for user ban
	def flood_person_ban(self, comment, body):
		index = body.find(' ')
		username = body[:index].replace('\\', '')
		body = body[index+1:]
		body = body.replace(' ', '')
		timeframe = int(body)
		
		# self.ban_user(username, timeframe)
		# self.usernote(username, 'Queueflooding '+str(timeframe)+' days.')
		# self.remove_k_flair(username)
		self.comment_reply(comment, 'This is where I would have banned ' + username + ' for ' + str(timeframe) + ' days. And I would have added the usernote: Queueflooding '+str(timeframe)+' days. And I would have removed the k flair.')


	# takes submission id
	# removes submission
	def remove_sm(self, submission):
		try:
			print('This is where I would have removed submission: ', str(submission))
			#self.reddit.submission(str(submission)).mod.remove()
		except Exception as e:
			print(e)
			pass


	# takes username, lower and upper boundary
	# removes all submissions between boundaries
	def mass_remove(self, username, B, A):
		done5 = False
		if min(A,B) == A:
			A-=1
			B+=1
		else:
			A+=1
			B-=1

		while done5 == False:
			try:
				confirm = "# Removed submissions\n\n| Submission | Removed |\n| --- | --- |"
				n=0
				
				for submission in self.reddit.redditor(username).submissions.new(limit=None):
					try:
						if submission.created_utc > min(A,B):
							if (submission.created_utc >= B and submission.created_utc <= A) or (submission.created_utc >= A and submission.created_utc <= B):
								if submission.subreddit.display_name == config.flooder_sub:
									self.remove_sm(submission)

									confirm = confirm + "\n| [{0}]({1})[.]({2}) | True |".format(submission.title, submission.permalink, submission.url)
									n+=1
								else:
									pass
							else:
								pass
						else:
							# break parsing
							break
					
					except Exception as e:
						print(e)
						pass

				done5 = True
				confirm = confirm + "\n\n Removed a total of {0} submissions.".format(n)

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

		return confirm


	# mainframe for removing user submissions
	def flood_person_remove(self, comment, body):
		body = body.replace(' ', '')
		timeframeA = calendar.timegm(time.strptime(body[:16], "%x%X"))

		body = body[16:]
		timeframeB = calendar.timegm(time.strptime(body[:16], "%x%X"))

		username = body[16:]

		msg = self.mass_remove(username, timeframeA, timeframeB)
		self.comment_reply(comment, msg)


	# checks comment stream
	# mainframe for commands when detected
	def commands(self):
		while True:
			try:
				for comment in self.check_subreddit.stream.comments(skip_existing=True):
					try:
						if comment.author.name in self.mod_team:
							if comment.body[:2] == '!f' and comment.body[:9] != '!flooders' and comment.body[:6] != '!fhelp' and comment.body[:3] != '!fb' and comment.body[:3] != '!fr' and comment.body[:3] != '!fp':
								self.flooders_main(comment, comment.body[3:])
							elif comment.body[:9] == '!flooders':
								self.flooders_main(comment, comment.body[10:])
							elif comment.body[:3] == '!fp' and comment.body[:8] != '!fperson':
								self.flood_person_main(comment, comment.body[4:])
							elif comment.body[:8] == '!fperson':
								self.flood_person_main(comment, comment.body[9:])
							elif comment.body[:3] == '!fb' and comment.body[:5] != '!fban':
								self.flood_person_ban(comment, comment.body[4:])
							elif comment.body[:5] == '!fban':
								self.flood_person_ban(comment, comment.body[6:])
							elif comment.body[:5] == '!frem' and comment.body[:8] != '!fremove':
								self.flood_person_remove(comment, comment.body[6:])
							elif comment.body[:8] == '!fremove':
								self.flood_person_remove(comment, comment.body[9:])
							elif comment.body[:6] == '!fhelp':
								self.comment_reply(comment, config.helpmessage)
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
