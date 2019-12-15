from prawcore.exceptions import RequestException, ResponseException, InvalidToken
from PIL import Image
import numpy as np
import requests
import asyncio
import config
import praw
import cv2
import os
import re


class bonk:
	# define variables
	def __init__(self):
		self.reddit = praw.Reddit(client_id = config.id, client_secret = config.secret, password = config.password, user_agent = config.user_agent, username = config.username)

		self.subreddit = self.reddit.subreddit(str(config.sub))

		self.path = os.path.dirname(os.path.abspath(__file__))


	# ignore future reports on a comment
	def ignore(self, comment_id):
		try:
			cm = self.reddit.comment(str(comment_id))
			cm.mod.ignore_reports()
		except Exception as e:
			print(e)
			pass


	# remove a comment
	def remove_comment(self, comment_id):
		try:
			cm = self.reddit.comment(str(comment_id))
			cm.mod.remove()
		except Exception as e:
			print(e)
			pass


	# approve a submission
	def approve_submission(self, comment_id):
		try:
			cm = self.reddit.comment(str(comment_id))
			sm = cm.submission
			sm.mod.approve()
		except Exception as e:
			print(e)
			pass


	# replies to comment
	def comment(self, comment_id):
		try:
			cm = self.reddit.comment(str(comment_id))
			cm.reply("Hmm seems like u/MAGIC_EYE_BOT made a mistake." + config.footer)
		except Exception as e:
			print(e)
			pass


	# mainframe for reverting magic eye actions
	def revert_magic_actions(self, comment_id):
		self.ignore(comment_id)
		self.remove_comment(comment_id)
		self.approve_submission(comment_id)
		self.comment(comment_id)


	# remove image from folder
	def remove_image(self, file_name):
		try:
			os.remove(self.path + r'\images' + '\\' + file_name)
		except Exception as e:
			print('Could not remove image; ', file_name, ' from images folder.')
			print(e)


	# initialize histogram arguments
	def initialize_histogram(self):
		h_bins = 50
		s_bins = 60

		h_ranges = [0, 180]
		s_ranges = [0, 256]

		return [h_bins, s_bins], h_ranges + s_ranges, [0, 1]


	# compares image histograms
	def comparing_histograms(self, repost_name, og_name):
		try:
			repost_img = cv2.imread(self.path + r'\images' + '\\' + repost_name)
			og_img = cv2.imread(self.path + r'\images' + '\\' + og_name)

			repost_hsv = cv2.cvtColor(repost_img, cv2.COLOR_BGR2HSV)
			og_hsv = cv2.cvtColor(og_img, cv2.COLOR_BGR2HSV)

			histSize, ranges, channels = self.initialize_histogram()

			repost_hist = cv2.calcHist(repost_hsv, channels, None, histSize, ranges, accumulate=False)
			# repost_hist = cv2.calcHist([repost_hsv], [0,1], None, [180,256], [0,180,0,256])
			cv2.normalize(repost_hist, repost_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
			og_hist = cv2.calcHist(og_hsv, channels, None, histSize, ranges, accumulate=False)
			# og_hist = cv2.calcHist([og_hsv], [0,1], None, [180,256], [0,180,0,256])
			cv2.normalize(og_hist, og_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

			return cv2.compareHist(repost_hist, og_hist, 0), cv2.compareHist(repost_hist, og_hist, 1), cv2.compareHist(repost_hist, og_hist, cv2.HISTCMP_BHATTACHARYYA)
			# return cv2.compareHist(repost_hist, og_hist, cv2.HISTCMP_BHATTACHARYYA)

		except Exception as e:
			print(e)
			pass


	async def save_img(self, url):
		file_name = url.split("/")
				
		if len(file_name) == 0:
			file_name = re.findall("/(.*?)", url)

		file_name = file_name[-1]

		if len(file_name) == 0:
			pass
		
		if "." not in file_name:
			file_name += ".jpg"

		r = requests.get(url)
		if file_name != '.jpg':
			with open(self.path + r'\images' + '\\' + file_name, "wb") as f:
				f.write(r.content)
		
			return file_name
		else:
			return False


	# saves pictures, calculates histograms
	async def save_calc_main(self, repost_link, og_link, comment_id):
		repost_name, og_name = await asyncio.gather(self.save_img(repost_link), self.save_img(og_link))
		
		if repost_name != False and og_name != False:
			a, b, c = self.comparing_histograms(repost_name, og_name)

			self.remove_image(repost_name)
			self.remove_image(og_name)

			if a != 1.0 and b != 0.0 and c != 0.0:
				self.revert_magic_actions(comment_id)
			else:
				pass

			#if int(a), int(b), int(c) != 1, 0, 0:
			#	self.revert_magic_actions(comment_id)

		else:
			if repost_name != False:
				self.remove_pic(repost_name)
			
			if og_name != False:
				self.remove_pic(og_name)


	# get magiceye comments
	def get_comments(self):
		while True:
			try:
				for comment in self.reddit.redditor('MAGIC_EYE_BOT').stream.comments(skip_existing=True):
					try:
						if comment.subreddit == config.sub:
							if "[Direct image link](" in comment.body:
								link = comment.body

								repost_link = link[link.find("Direct image link")+19:link.find("Direct image link")+19+link[link.find("Direct image link")+19:].find(")")]
								og_link = comment.submission.url

								asyncio.get_event_loop().run_until_complete(self.save_calc_main(repost_link=repost_link, og_link=og_link, comment_id=comment.id))
						else:
							continue

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

						self.path = os.path.dirname(os.path.abspath(__file__))
							
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

				self.path = os.path.dirname(os.path.abspath(__file__))
					
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


	def main(self):
		self.get_comments()


if __name__ == '__main__':
	bonk().main()
