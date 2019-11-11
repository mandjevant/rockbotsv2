from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import pickle as cPickle
import threading
import datetime
import operator
import sqlite3
import config
import praw
import time
import re


class bot:
	# defined variables
	def __init__(self):
		self.reddit = praw.Reddit(client_id = config.id, client_secret = config.secret, password = config.password, user_agent = config.user_agent, username = config.username)	
		self.subreddit = self.reddit.subreddit(str(config.sub))

		self.db_conn = self.initiate_database()


	###########################################################################
	# Section 1
	# This section contains database actions
	# Function 1.1; initiate database tables
	# Function 1.2; insert new comment row in database
	# Function 1.3; update votes column in comment row
	# Function 1.4; remove row from comment database
	###########################################################################


	# initiates database
	def initiate_database(self):
		try:
			conn = sqlite3.connect('insane.db', check_same_thread=False)
			conn.execute(
				'''
				CREATE TABLE IF NOT EXISTS COMMENTS (
				COMMENT_ID VARCHAR(20) PRIMARY KEY,
				VOTES_DICT BLOB,
				SUB_CREATED FLOAT,
				EXPLANATION STRING
				);'''
			)
			return conn
			print('Connected to SQLITE database ' + sqlite3.version)
		except sqlite3.Error as e:
			print('Failed to connect to database')
			print(e)


	# insert new comment row in COMMENT database
	def insert_in_db(self, comment_id, votes={}):
		try:
			vote_data = cPickle.dumps(votes, cPickle.HIGHEST_PROTOCOL)
			params = (str(comment_id), sqlite3.Binary(vote_data), comment_id.submission.created_utc, 'False')
			self.db_conn.execute("INSERT INTO COMMENTS (COMMENT_ID,VOTES_DICT,SUB_CREATED,EXPLANATION) VALUES (?,:data,?,?)", params)
			self.db_conn.commit()
		except sqlite3.Error as e:
			print('Failed to create row')
			print(e)


	# update votes dict in COMMENT database row
	def update_in_db(self, comment_id, votes={}):
		try:
			vote_data = cPickle.dumps(votes, cPickle.HIGHEST_PROTOCOL)
			params = (sqlite3.Binary(vote_data), str(comment_id))
			self.db_conn.execute("UPDATE COMMENTS SET VOTES_DICT = :data WHERE COMMENTS.COMMENT_ID=?", params)
			self.db_conn.commit()
		except sqlite3.Error as e:
			print('Failed to update row')
			print(e)


	# update explanation boolean in COMMENT database row
	def update_explan_db(self, comment_id, bot_cm):
		try:
			params = (str(comment_id), str(bot_cm))
			self.db_conn.execute("UPDATE COMMENTS SET EXPLANATION = ? WHERE COMMENTS.COMMENT_ID=?", params)
			self.db_conn.commit()
		except sqlite3.Error as e:
			print('Failed to update row')
			print(e)


	# remove row from COMMENT database
	def remove_from_db(self, comment_id):
		try:
			cr = self.db_conn.cursor()
			cr.execute("DELETE FROM COMMENTS WHERE COMMENTS.COMMENT_ID='%s'" %str(comment_id))
			self.db_conn.commit()
		except sqlite3.Error as e:
			print('Failed to remove row')
			print(e)


	###########################################################################
	# Section 2
	# This section contains user actions
	# Function 2.1; report submission
	# Function 2.2; removes comment
	# Function 2.3; removes submission
	# Function 2.4; comments on submission
	# Function 2.5; updates comment
	# Function 2.6; locks comment
	# Function 2.7; last update comment
	# Function 2.8; deletes own comment
	###########################################################################


	# reports submission
	def report_submission(self, submission, message):
		try:
			self.reddit.submission(submission).report(message)
		except Exception as e:
			print(e.response.content)
			pass


	# removes comment
	def remove_comment(self, comment):
		try:
			self.reddit.comment(str(comment)).mod.remove()
		except Exception as e:
			print(e.response.content)
			pass
	

	# remove submission
	def remove_submission(self, submission):
		try:
			self.reddit.submission(submission).mod.remove()
			self.reddit.submission(submission).mod.send_removal_message('Your submission was removed because the voting system deemed it: fake')
		except Exception as e:
			print(e.response.content)
			pass


	# comments on submission
	def comment(self, submission):
		try:
			cm = submission.reply(config.initial_comment + '\n\n Hey OP, if you provide further information in a comment, make sure to start your comment with !explanation.')
			cm.mod.distinguish(sticky=True)
			self.insert_in_db(cm)
		except Exception as e:
			print(e)
			pass


	# updates comment
	def update_comment(self, comment_id, insane, notinsane, fake, explan):
		if explan == 'False':
			try:
				#self.reddit.comment(str(comment_id)).edit(config.initial_comment + "\n\n # Votes \n\n| Insane | Not insane | Fake |\n| --- | --- | --- |\n| {0} | {1} | {2} |".format(insane, notinsane, fake) + config.footer)
				self.reddit.comment(str(comment_id)).edit(config.initial_comment + "\n\n # Votes \n\n| Insane | Not insane | Fake |\n| --- | --- | --- |\n| {0} | {1} | {2} |".format(insane, notinsane, fake) + '\n\n Hey OP, if you provide further information in a comment, make sure to start your comment with !explanation. \n' + config.footer)
			except Exception as e:
				print(e)
				pass
		else:
			try:
				foot = "\n\n\n\n\n\nOP has provided further information [in this comment]({0}).".format(explan)
				self.reddit.comment(str(comment_id)).edit(config.initial_comment + "\n\n # Votes \n\n| Insane | Not insane | Fake |\n| --- | --- | --- |\n| {0} | {1} | {2} |".format(insane, notinsane, fake) + foot)
				#self.reddit.comment(str(comment_id)).edit(config.initial_comment + "\n\n # Votes \n\n| Insane | Not insane | Fake |\n| --- | --- | --- |\n| {0} | {1} | {2} |".format(insane, notinsane, fake) + '\n\n Hey OP, if you provide further information in a comment, make sure to start your comment with !explanation. \n' + config.footer)
			except Exception as e:
				print(e)
				pass


	# locks comment
	def lock_comment(self, comment_id):
		try:
			self.reddit.comment(str(comment_id)).mod.lock()
		except Exception as e:
			print(e)
			pass


	# last update comment
	def last_update_comment(self, comment_id, insane, notinsane, fake, explan):
		insane = int(insane)
		notinsane = int(notinsane)
		fake = int(fake)

		if insane > notinsane and insane > fake:
			winner = 'insane'
			winner_count = str(insane)
		elif fake > notinsane and fake > insane:
			winner = 'fake'
			winner_count = str(fake)
		elif notinsane > insane and notinsane > fake:
			winner = 'not insane'
			winner_count = str(notinsane)
		else:
			winner = 'insane'
			winner_count = str(insane)

		if explan == 'False':
			try:
				self.reddit.comment(str(comment_id)).edit(config.final_comment + winner + " with " + str(winner_count) + " votes \n\n # Votes \n\n| Insane | Not insane | Fake |\n| --- | --- | --- |\n| {0} | {1} | {2} |".format(insane, notinsane, fake) + config.footer)
			except Exception as e:
				print(e)
				pass
		else:
			try:
				foot = "\n\n\n\n\n\nOP has provided further information [in this comment]({0}).".format(explan)
				self.reddit.comment(str(comment_id)).edit(config.final_comment + winner + " with " + str(winner_count) + " votes \n\n # Votes \n\n| Insane | Not insane | Fake |\n| --- | --- | --- |\n| {0} | {1} | {2} |".format(insane, notinsane, fake) + foot)
			except Exception as e:
				print(e)
				pass


	# update submission flair with removed flair
	def removed_flair(self, submission):
		try:
			self.reddit.submission(submission).mod.flair(text='Removed; Fake through voting',css_class='removedvote')
		except Exception as e:
			print(e)
			pass


	# delete own comment
	def delete_own_comment(self, comment):
		try:
			self.reddit.comment(comment).delete()
		except Exception as e:
			print(e.response.content)
			pass


	###########################################################################
	# Section 3
	# This section contains legitimacy checks and random functions
	# Function 3.1; regex to check for votes
	# Function 3.2; act on votes
	###########################################################################


	# checks if a vote is legit
	def legit_vote(self, body):
		low_body = body.lower()

		if re.match("i\s*n\s*s\s*a\s*n\s*e", low_body):
			return 'insane'
		elif re.match("\s*n\s*o\s*t\s*i\s*n\s*s\s*a\s*n\s*e", low_body):
			return 'not insane'
		elif re.match("\s*f\s*a\s*k\s*e", low_body):
			return 'fake'
		else:
			return None


	# act on votes 
	def act_on_votes(self, insane, notinsane, fake, submission):
		insane = int(insane)
		notinsane = int(notinsane)
		fake = int(fake)

		if insane > notinsane and insane > fake:
			maxi = 'insane'
		elif fake > notinsane and fake > insane:
			maxi = 'fake'
		elif notinsane > insane and notinsane > fake:
			maxi = 'not insane'
		else:
			maxi = 'insane'

		#if maxi == 'insane':
			#self.report_submission(submission, "Submission deemed 'insane' through voting. Please flair it properly.")
		if maxi == 'not insane':
			self.report_submission(submission, "Submission deemed 'not insane' through voting.")
		elif maxi == 'fake':
			self.removed_flair(submission)
			self.report_submission(submission, 'Please review this submission. It was removed because it was deemed fake through the voting system.')
			self.remove_submission(submission)


	###########################################################################
	# Section 4
	# This section contains bot commands
	# Function 4.1; removes submission
	# Function 4.2; locks submission
	# Function 4.3; comments on submission
	# Function 4.4; parses !comment command
	# Function 4.5; parses !lock command
	# Function 4.6; parses !remove command
	# Function 4.7; parses !hotlines command
	###########################################################################


	# takes submission id, removes submission
	def remove_sm(self, submission_id, reason):
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


	# takes submission id, comments on submission
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
		self.remove_comment(cm_id)
		self.sm_lock(sm_id)
		self.comment_comm(sm_id, reason)


	# parses comment for ~!comment~ command
	def comment_parse(self, body, cm_id, sm_id):
		reason = body[9:]
		self.remove_comment(cm_id)
		self.comment_comm(sm_id, reason)


	# parses comment for ~!remove~ command
	def remove_parse(self, body, cm_id, sm_id):
		reason = body[8:]
		self.remove_comment(cm_id)
		self.remove_sm(sm_id, reason)


	# sticky comment with suicide and abuse support lines
	def hotline_parse(self, body, cm_id, sm_id):
		reason = config.hotline
		self.remove_comment(cm_id)
		self.comment_comm(sm_id, reason)


	###########################################################################
	# Section 5
	# This section contains threading actions
	# Function 5.1; submission stream
	# Function 5.2; database evaluation
	# Function 5.3; threading
	###########################################################################


	# submission stream
	def submissions(self):
		for submission in self.subreddit.stream.submissions(skip_existing=True):
			try:
				self.comment(submission)
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


	# evaluates comments in database
	def evaluation(self):
		while True:
			try:
				cursor = self.db_conn.execute("SELECT * FROM COMMENTS")

				for i in cursor.fetchall():
					votes = cPickle.loads(i[1])
					comment = self.reddit.comment(str(i[0]))
					explan = i[3]

					if time.time() - comment.created_utc > 60*60*config.maxtime:
						self.remove_from_db(comment.id)

						insane = sum(value == 'insane' for value in votes.values())
						notinsane = sum(value == 'not insane' for value in votes.values())
						fake = sum(value == 'fake' for value in votes.values())
						total = insane + notinsane + fake

						self.last_update_comment(str(comment.id), str(insane), str(notinsane), str(fake), str(explan))
						self.lock_comment(str(comment.id))

						self.act_on_votes(str(insane), str(notinsane), str(fake), comment.submission.id)
					else:
						comment.reply_sort = 'new'
						comment = comment.refresh()
						replies = comment.replies

						for reply in replies:
							try:
								if reply.parent().author.name == config.username:
									if reply.author.name not in votes.keys():
										legit = self.legit_vote(reply.body)
										if legit != None:
											try:
												votes.update({reply.author.name:legit})
												reply.upvote()
												self.remove_comment(reply)
											except Exception as e:
												print(e)
										else:
											pass
									else:
										pass
								else:
									pass
							except Exception as e:
								print(e)

						self.update_in_db(str(comment.id), votes)

						insane = sum(value == 'insane' for value in votes.values())
						notinsane = sum(value == 'not insane' for value in votes.values())
						fake = sum(value == 'fake' for value in votes.values())

						self.update_comment(str(comment.id), str(insane), str(notinsane), str(fake), str(explan))

				minute = datetime.datetime.now().minute
		
				if minute > 30:
					minute = minute - 30

				time.sleep(60*(30-minute))

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


	# runs bot commands when command is detected 
	def commands(self):
		while True:
			try:
				mod_team = [x for x in self.subreddit.moderator()]

				for comment in self.subreddit.stream.comments(skip_existing=True):
					if comment.body[:8] == '!disable':
						try:
							if comment.author.name in mod_team:
								self.remove_from_db(comment.parent_id[3:])
								self.delete_own_comment(comment.parent_id[3:])
							else:
								pass
						except Exception as e:
							print(e)
							pass

					elif comment.body[:12] == '!explanation':
						try:
							if comment.author.name == comment.submission.author.name:
								sm = comment.submission
								sm.comment_sort = 'new'
								cms = sm.comments.list()
								
								bot_cm = False
								for cm in cms:
									try:
										if cm.author.name == config.username:
											bot_cm = cm.id
											break
										else:
											continue
									except Exception as e:
										print(e)
										pass

								if bot_cm != False:
									self.update_explan_db(comment.permalink, bot_cm)
									
									cursor = self.db_conn.cursor().execute("SELECT * FROM COMMENTS WHERE COMMENTS.COMMENT_ID='%s'" %str(bot_cm))
									i = cursor.fetchone()
									votes = cPickle.loads(i[1])
									comment = self.reddit.comment(str(i[0]))
									explan = i[3]

									comment.reply_sort = 'new'
									comment = comment.refresh()
									replies = comment.replies

									for reply in replies:
										try:
											if reply.parent().author.name == config.username:
												if reply.author.name not in votes.keys():
													legit = self.legit_vote(reply.body)
													if legit != None:
														try:
															votes.update({reply.author.name:legit})
															reply.upvote()
															self.remove_comment(reply)
														except Exception as e:
															print(e)
													else:
														pass
												else:
													pass
											else:
												pass
										except Exception as e:
											print(e)

									self.update_in_db(str(bot_cm), votes)

									insane = sum(value == 'insane' for value in votes.values())
									notinsane = sum(value == 'not insane' for value in votes.values())
									fake = sum(value == 'fake' for value in votes.values())

									self.update_comment(str(comment.id), str(insane), str(notinsane), str(fake), str(explan))
								else:
									comment.reply('Could not sticky explanation. Apologies for the inconvenience.' + config.footer)

							else:
								pass
						except Exception as e:
							print(e)
							pass

					elif comment.body[:5] == '!lock':
						try:
							if comment.author.name in mod_team:
								self.lock_parse(comment.body, comment.id, comment.submission.id)
							else:
								pass
						except Exception as e:
							print(e)
							pass

					elif comment.body[:8] == '!comment':
						try:
							if comment.author.name in mod_team:
								self.comment_parse(comment.body, comment.id, comment.submission.id)
							else:
								pass
						except Exception as e:
							print(e)
							pass

					elif comment.body[:7] == '!remove':
						try:
							if comment.author.name in mod_team:
								self.remove_parse(comment.body, comment.id, comment.submission.id)
							else:
								pass
						except Exception as e:
							print(e)
							pass

					elif comment.body[:8] == '!hotline':
						try:
							if comment.author.name in mod_team:
								self.hotline_parse(comment.body, comment.id, comment.submission.id)
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


	# threading to execute functions in parallel
	def threading(self):
		a = threading.Thread(target=self.submissions, name='Thread-a', daemon=True)
		b = threading.Thread(target=self.evaluation, name='Thread-b', daemon=True)
		c = threading.Thread(target=self.commands, name='Thread-c', daemon=True)

		a.start()
		b.start()
		c.start()

		a.join()
		b.join()
		c.join()


if __name__ == '__main__':
	bot().threading()
