id = '' # enter user ID
secret = '' # enter user secret ID
username = '' # enter user username
password = '' # enter user password
user_agent = 'rareinsultsbot/0.2 by Mandjevant' # user agent

sub = 'rareinsults' # subreddit
threshold = 75 # number of upvotes post should get to change to muscle message
downvotethreshold = 4 # number of downvotes post should get before it is removed

comment_message = "Upvote this comment if you feel this submission is characteristic of our subreddit. Downvote this if you feel that it is not. If this comment's score falls below a certain number, this submission will be automatically removed." # standard comment message
removal_message = 'This submission has been removed because the stickied bot comment reached the downvote threshold. Please contact the moderation team if you have questions regarding this removal.' # the body of the message
removal_title = 'Removed submission' # The short reason given in the message. (Ignored if type is ‘public’.)
removal_type = 'public' # One of ‘public’, ‘private’, ‘private_exposed’. ‘public’ leaves a stickied comment on the post. ‘private’ sends a Modmail message with hidden username. ‘private_exposed’ sends a Modmail message without hidden username
upvote_threshold_message = 'Nice.' # message sent as upvote threshold is read

database_name = 'rareinsults.db'
