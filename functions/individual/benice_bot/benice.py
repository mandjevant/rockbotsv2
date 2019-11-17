from prawcore.exceptions import RequestException, ResponseException, InvalidToken
import threading
import sqlite3
import config
import random
import praw
import time


class benice:
	# defining variables
	def __init__(self):
		self.reddit = praw.Reddit(client_id = config.id, client_secret = config.secret, password = config.password, user_agent = config.user_agent, username = config.username)

		self.subreddit = self.reddit.subreddit(str(config.sub))

		self.gold_responses = config.gold_responses
		self.good_comments = config.good_comments
		self.banned_list = config.banned_list

		self.silverwait = 86400 / config.golds_per_day
		self.start_time = 0
		self.db_connection = self.initiate_database()


	def initiate_database(self):
		try:
			conn = sqlite3.connect('benice.db', check_same_thread=False)
			conn.execute(
				'''CREATE TABLE IF NOT EXISTS COMMENTS (
					COMMENT_ID VARCHAR(20) PRIMARY KEY
				);'''
			)
			return conn
			print("Connected to SQLITE database " + sqlite3.version)
		except Error as e:
			print("Failed to connect to database")
			print(e)


	# inserts id in database
	def insert_in_db(self, comment_id):
		self.db_connection.execute("INSERT INTO COMMENTS (COMMENT_ID) VALUES ('%s')" %(str(comment_id)) )
		self.db_connection.commit()


	# removes entry from database
	def remove_from_db(self, comment_id):
		try:
			cr = self.db_connection.cursor()
			cr.execute("DELETE FROM COMMENTS WHERE COMMENTS.COMMENT_ID='%s'" %str(comment_id))
			self.db_connection.commit()
		except sqlite3.Error as e:
			print('Failed to remove from database')
			print(e)


	# takes fullname of item and gilding message
	# gilds item
	def gild_item(self, fullname, message):
		try:
			self.reddit.post("/api/v1/gold/gild/" + fullname, data={"gildings":"gid_1", "isAnonymous":False, "message":message})
		except Exception as e:
			print(e.response.content)


	# takes comment ID to remove the comment
	def comment_remove(self, comment):
		try:
			self.reddit.comment(comment).delete()
		except:
			print('Failed to remove comment; ', comment)


	# takes message and item, replies to item with message 
	def reply(self, item, message):
		try:
			commentid = item.reply(message + config.footer)
			self.insert_in_db(commentid)
		except:
			print('Could not reply to item; ', item, ' with message; ', message)


	# takes comment, awards gold and responds with silver response
	def silverResponse(self, comment):
		try:
			commentid = comment.reply(random.choice(self.gold_responses) + config.footer)
			self.insert_in_db(commentid)
			self.gild_item(comment.fullname, "Have a great day!\n\n\n\n-From u/I_Love_You-bot")
		except:
			print('Function; ' + 'silverResponse' + ' did not function as expected.')


	# item evaluations
	def evaluation(self, item):
		try:
			if str(item.subreddit) not in self.banned_list:
				if self.reddit.subreddit(str(item.subreddit)).over18 == False:
					if 'i_love_you-bot' in item.body.lower():
						self.reply(item, config.ping_response)
					elif 'i love you' in item.body.lower():
						self.reply(item, config.love_you_response)
					elif 'good bot' in item.body.lower():
						self.reply(item, config.good_bot_response)
					elif 'bad bot' in item.body.lower():
						self.reply(item, config.bad_bot_response)

					for i in config.good_messages:
						if i in item.body.lower():
							chance = random.random()
							if chance < 0.0075 and chance > 0.0010001:
								self.normalResponse(item)
							elif chance < 0.001:
								if (time.time() - self.start_time) > self.silverwait:
									self.silverResponse(item)
									self.start_time = time.time()
		except:
			pass


	# access submission stream
	def submissions(self):
		try:
			for submission in self.subreddit.stream.comments(skip_existing=True):
				self.evaluation(submission)

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


	# access comment stream
	def comments(self):
		try:
			for comment in self.subreddit.stream.submissions(skip_existing=True):
				self.evaluation(comment)

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
		


	# iterates over comment ids in database
	def past_comments(self):
		try:
			start_time = time.time()

			while True:
				cursor = self.db_connection.execute("SELECT * FROM COMMENTS")
				for i in cursor.fetchall():
					comment = self.reddit.comment(i[0])
					try:
						score = comment.score
						if score <= -config.downvote_threshold:
							self.comment_remove(comment)
							self.remove_from_db(comment.id)
						else:
							continue
					except:
						print('not able to fetch comment score or smth')
				
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


	# threading to execute functions in parallel
	def threading(self):
		a = threading.Thread(target=self.submissions, name='Thread-a', daemon=True)	
		b = threading.Thread(target=self.comments, name='Thread-b', daemon=True)
		c = threading.Thread(target=self.past_comments, name='Thread-c', daemon=True)

		a.start()																		
		b.start()																		
		c.start()

		a.join()																		
		b.join()
		c.join()


if __name__ == '__main__':
	benice().threading()
