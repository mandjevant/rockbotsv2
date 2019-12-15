from prawcore.exceptions import RequestException, ResponseException, InvalidToken
from datetime import datetime
from down_detect import bot
from bonk import bonkers
import asyncio
import discord
import config
import praw


event_loop = asyncio.get_event_loop()
discord_client = discord.Client(loop=event_loop)


def main():
	event_loop.create_task(reddit_stream())
	discord_client.run(config.discord_id)


async def reddit_stream():
	print('entered reddit_stream')
	ids = set()
	await discord_client.wait_until_ready()

	while True:
		try:
			reddit = praw.Reddit(username = config.username,password = config.password,client_id = config.id,client_secret = config.secret,user_agent = config.user_agent)
			subreddit = reddit.subreddit(config.sub)

			for comment in reddit.redditor('MAGIC_EYE_BOT').comments.new(limit=5):
				if comment.id in ids:
					break
				else:
					try:
						ids.add(comment.id)
						if comment.subreddit == config.sub:
							if "[Direct image link](" in comment.body:
								link = comment.body

								repost_link = link[link.find("Direct image link")+19:link.find("Direct image link")+19+link[link.find("Direct image link")+19:].find(")")]
								og_link = comment.submission.url

								send_message = bonkers().save_calc_main(repost_link=repost_link, og_link=og_link, comment_id=comment.id)

								if send_message == True:
									embeda = discord.Embed(description="This is the original image. <{0}>".format("http://www.reddit.com"+comment.submission.permalink), color=13900434, timestamp=datetime.now())
									embeda.set_footer(text="I'm a bot", icon_url="https://styles.redditmedia.com/t5_2zmfe/styles/communityIcon_d08xy4s3ol241.png")
									embeda.set_image(url=og_link)

									embedb = discord.Embed(description="This is the identified repost.", color=13900434, timestamp=datetime.now())#.strftime("%m/%d/%Y, %H:%M:%S"))
									embedb.set_footer(text="I'm a bot", icon_url="https://styles.redditmedia.com/t5_2zmfe/styles/communityIcon_d08xy4s3ol241.png")
									embedb.set_image(url=repost_link)

									ch = discord_client.get_channel(655095324863496279)
									await ch.send(content="Hey! I just found a possible Magic Eye mistake. Please check if this is a repost or not. \nIf this is a repost, cool. If it's not a repost, type `$revert` below.\n\n", embed=embeda)
									await ch.send(embed=embedb)
						else:
							continue

					except InvalidToken:
						print("Encountered Invalid Token error, resetting PRAW")
						time.sleep(10)
						reddit = None
						reddit = praw.Reddit(username = config.username,
											  password = config.password,
											  client_id = config.id,
											  client_secret = config.secret,
										  	  user_agent = config.user_agent)
						subreddit = reddit.subreddit(str(config.sub))

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

			await asyncio.sleep(5)

		except InvalidToken:
			print("Encountered Invalid Token error, resetting PRAW")
			time.sleep(10)
			reddit = None
			reddit = praw.Reddit(username = config.username,
								  password = config.password,
								  client_id = config.id,
								  client_secret = config.secret,
							  	  user_agent = config.user_agent)
			subreddit = reddit.subreddit(str(config.sub))

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


@discord_client.event
async def on_ready():
	print('We have logged in as {0}'.format(discord_client.user))


@discord_client.event
async def on_message(message):
	if message.content.startswith('$revert'):
		link = message.content[len('$revert')+1:]
		
		try:
			reddit = praw.Reddit(username = config.username,password = config.password,client_id = config.id,client_secret = config.secret,user_agent = config.user_agent)
			submission = reddit.submission(url=link)
			submission.mod.approve()

			comments = submission.comments
			for comment in comments:
				if comment.author == 'MAGIC_EYE_BOT':
					comment.reply("Whoops, bot made a mistake. I approved the submission and now it's back online.")
					comment.mod.remove()
					break
				else:
					continue

			await message.channel.send('Magic eye actions on {0} reverted.'.format(link))
		except Exception as e:
			print(e)
			await message.channel.send('Could not revert magic eye actions on {0}'.format(link))
		
	elif message.content.startswith('$down'):
		last_flair_utc, last_comment_utc, bot_2_online = bot().main()
		text = "**I checked the bots and this is what I found:**\n\n"

		if last_flair_utc - last_comment_utc > 300:
			text += "u/{0} aka flairbot is offline :negative_squared_cross_mark:\n".format(config.bot_username)
		else:
			text += "u/{0} aka flairbot is online :white_check_mark:\n".format(config.bot_username)

		if bot_2_online == True:
			text += "u/{0} aka community bot is either stuck or offline :negative_squared_cross_mark:".format(config.bot_username_2)
		else:
			text += "u/{0} aka community bot is online :white_check_mark:".format(config.bot_username_2)

		await message.channel.send(text)

	elif message.content.startswith('$approve'):
		username = message.content[len('$approve')+1:]
		try:
			reddit = praw.Reddit(username = config.username,password = config.password,client_id = config.id,client_secret = config.secret,user_agent = config.user_agent)
			subreddit = reddit.subreddit(str(config.sub))
			subreddit.contributor.add(username)

			await message.channel.send('Added {0} as an approved user to r/{1}'.format(str(username), str(config.sub)))
		except Exception as e:
			print(e)
			await message.channel.send('Could not add {0} as an approved user to r/{1}'.format(str(username), str(config.sub)))


if __name__ == '__main__':
	main()
