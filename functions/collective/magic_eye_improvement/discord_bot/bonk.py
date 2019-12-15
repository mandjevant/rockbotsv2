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


class bonkers:
	# define variables
	def __init__(self, config=config):
		self.reddit = praw.Reddit(client_id = config.id, client_secret = config.secret, password = config.password, user_agent = config.user_agent, username = config.username)

		self.subreddit = self.reddit.subreddit(str(config.sub))

		self.path = os.path.dirname(os.path.abspath(__file__))


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


	#async def save_img(self, url):
	def save_img(self, url):
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


 	# main of pic saving and histogram calculation and comparison
	def save_calc_main(self, repost_link, og_link, comment_id):
		try:
			#repost_name, og_name = await asyncio.gather(self.save_img(repost_link), self.save_img(og_link))
			repost_name = self.save_img(repost_link)
			og_name = self.save_img(og_link)
			
			if repost_name != False and og_name != False:
				a, b, c = self.comparing_histograms(repost_name, og_name)
				print(a,b,c)

				self.remove_image(repost_name)
				self.remove_image(og_name)

				if a < 0.99 and b != 0.0 and c != 0.0:
					return True
				else:
					return False

			else:
				if repost_name != False:
					self.remove_pic(repost_name)
					return False
				
				if og_name != False:
					self.remove_pic(og_name)
					return False
		
		except Exception as e:
			print(e)
			return False


if __name__ == '__main__':
	bonk().save_calc_main()
