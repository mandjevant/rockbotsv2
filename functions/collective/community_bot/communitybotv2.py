from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import praw
import time
import threading
import config
import sqlite3


class bot():
	# define variables
	def __init__(self):
		self.reddit = praw.Reddit(username = config.username,
								  password = config.password,
								  client_id = config.id,
								  client_secret = config.secret,
							  	  user_agent = config.user_agent)

		self.subreddit = self.reddit.subreddit(str(config.sub))
		self.db_connection = self.initiate_database()
		self.mod_list = [x for x in self.subreddit.moderator()]


	# creates connection to database
	def initiate_database(self):
		try:
			conn = sqlite3.connect(config.database_name, check_same_thread=False)
			conn.execute(
				'''CREATE TABLE IF NOT EXISTS COMMENTS (
					COMMENT_ID VARCHAR(20) PRIMARY KEY
				);'''
			)
			return conn
			print('Connected to SQLITE database ' + sqlite3.version)
		except sqlite3.Error as e:
			print('Failed to connect to database')
			print(e)


	# inserts comment id in database
	def insert_in_db(self, comment_id):
		try:
			self.db_connection.execute("INSERT INTO COMMENTS (COMMENT_ID) VALUES ('%s')" %(str(comment_id)))
			self.db_connection.commit()
		except Exception as e:
			print(e)


	# removes entry from database
	def remove_from_db(self, comment_id):
		try:
			cr = self.db_connection.cursor()
			cr.execute("DELETE FROM COMMENTS WHERE COMMENTS.COMMENT_ID='%s'" %str(comment_id))
			self.db_connection.commit()
		except sqlite3.Error as e:
			print('Failed to remove from database')
			print(e)


	# reports submission
	def report_submission(self, submission):
		try:
			submission.report('Please review this submission. It exceeded the downvote threshold.')
		except Exception as e:
			print(e.response.content)
			pass


	# takes comment, edits comment with muscle message
	def edit_comment(self, comment):
		try:
			comment.edit(config.upvote_threshold_message)
		except Exception as e:
			print(e)
			pass


	# takes submission ID to remove the submission
	def post_remove(self, submission):
		try:
			self.find_sticky(submission)
			submission.mod.remove()																						
			submission.mod.send_removal_message(message = config.removal_message, 
												title = config.removal_title, 
												type = config.removal_type)
		except Exception as e:
			print(e)
			pass


	# unstickies comment
	def unsticky(self, comment): 
		try:
			comment.mod.distinguish(how='yes', sticky=False)
		except Exception as e:
			print(e)


	def find_sticky(self, submission):
		for comment in submission.comments:
			if comment.stickied == True:
				self.unsticky(comment)
			else:
				continue


	# takes submission ID to reply to in the form of a comment
	# returns the comment ID
	def comment(self, submission):
		try: 
			sm = submission.reply(config.comment_message)
			sm.mod.distinguish(sticky=True)
			self.insert_in_db(sm)
		except Exception as e:
			print(e)
			pass


	# creates list of contributors, returns list
	def contributors(self):
		contributors = list()
		for contributor in self.subreddit.contributor():
			contributors.append(contributor)

		return contributors


	# main part of bot
	def submission_handling(self, submission):
		contributorlist = self.contributors()

		if submission.author not in contributorlist:
			self.comment(submission)
		else:
			pass


	# takes submission id, removes submission
	def sm_remove(self, submission_id, reason):
		try:
			submission = self.reddit.submission(str(submission_id))
			submission.mod.remove()																						
			submission.mod.send_removal_message(message = reason, 
												title = 'Submission removed', 
												type = config.removal_type)
		except Exception as e:
			print(e)
			pass


	# takes submission id, locks submission
	def sm_lock(self, submission_id):
		try:
			self.reddit.submission(str(submission_id)).mod.lock()
		except Exception as e:
			print(e)
			pass


	# takes comment id, removes comment
	def remove_cm(self, comment_id):
		try:
			self.reddit.comment(str(comment_id)).mod.remove()
		except Exception as e:
			print(e)
			pass


	# takes submission id, replies to submission
	def comment_comm(self, submission_id, reason):
		try:
			cm = self.reddit.submission(str(submission_id)).reply(reason)
			cm.mod.distinguish(how='yes', sticky=True)
		except Exception as e:
			print(e)
			pass


	# parses comment for ~!lock~ command 
	def lock_parse(self, body, cm_id, sm_id):
		reason = body[6:]
		self.remove_cm(cm_id)
		self.sm_lock(sm_id)
		self.comment_comm(sm_id, reason)


	# parses comment for ~!comment~ command
	def comment_parse(self, body, cm_id, sm_id):
		reason = body[9:]
		self.remove_cm(cm_id)
		self.comment_comm(sm_id, reason)


	# removes stickied comment from db
	def rem_sticky(self, submission_id):
		try:
			submission = self.reddit.submission(str(submission_id))
			for comment in submission.comments:
				if comment.stickied == True:
					self.remove_from_db(comment)
					pass
				else:
					continue
		except Exception as e:
			print(e)
			pass


	# parses comment for ~!remove~ command
	def remove_parse(self, body, cm_id, sm_id):
		reason = body[8:]
		self.remove_cm(cm_id)
		self.sm_remove(sm_id, reason)
		self.rem_sticky(sm_id)


	# checks comment stream for commands
	def comment_check(self):
		while True:
			try:
				for comment in self.subreddit.stream.comments(skip_existing=True):
					mod_list = [x for x in self.subreddit.moderator()]
					if comment.author in mod_list:
						if '!lock' == comment.body[:5]:
							self.lock_parse(comment.body, comment.id, comment.submission.id)
						elif '!comment' == comment.body[:8]:
							self.comment_parse(comment.body, comment.id, comment.submission.id)
						elif '!remove' in comment.body[:7]:
							self.remove_parse(comment.body, comment.id, comment.submission.id)
						else:
							pass
					else:
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
	

	# accesses submission stream
	def submissions(self):
		while True:
			try:
				for submission in self.subreddit.stream.submissions(skip_existing=True):
					self.submission_handling(submission)

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


	# checks score on comments in database
	def past_comments(self):
		try:
			start_time = time.time()

			while True:
				cursor = self.db_connection.execute("SELECT * FROM COMMENTS")
				for i in cursor.fetchall():
					comment = self.reddit.comment(i[0])
					score = comment.score
					if score <= -config.downvotethreshold:
						self.post_remove(comment.submission)
						self.report_submission(comment.submission)
						self.remove_from_db(i[0])
					elif score >= config.threshold:
						self.edit_comment(comment)
						self.remove_from_db(i[0])
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


	# uses threading to execute functions in parallel
	def threading(self):
		a = threading.Thread(target=self.submissions, name='Thread-a', daemon=True)		
		b = threading.Thread(target=self.past_comments, name='Thread-b', daemon=True)
		c = threading.Thread(target=self.comment_check, name='Thread-c', daemon=True)
		
		a.start()																		
		b.start()																	
		c.start()	
		
		a.join()																		
		b.join()
		c.join()
		

if __name__ == '__main__':
	bot().threading()
