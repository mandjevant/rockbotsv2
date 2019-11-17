id = '' # enter user ID
secret = '' # enter user secret ID
username = '' # enter user username
password = '' # enter user password	
user_agent = 'Flairbot/0.1 by Mandjevant' # user agent

sub = '' # subreddit
time_removal = 1800 # time between flair reminder and submission removal
time_flair = 180 # time between submitted and flair reminder

flair_message = ('Your post does not have a flair and will soon be removed. Please add a flair within ' + str(int(time_removal/60)) + ' minutes or your post will be removed. This was an automated action by the r/'+ sub +' moderation team.') # flair message
removal_message = ('Your post was removed because a flair was not set in time.') # removal message
removal_title = ('No flair') # title of removal message
