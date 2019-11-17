id = '' # enter user ID
secret = '' # enter user secret ID
username = '' # enter user username
password = '' # enter user password
user_agent = '' # user agent
sub = '' # name of sub


rules = {'Nigger': ['remove', False], # add rules in the form {word: [action, regex]}
		 "kys": ['report', True],
		 "(kill?|end|hang|neck) (yo)?ur ?sel(f|ve)s?": ['report', True],
		 "commit\\s*suicide": ['report', True],
		 "I\\s*hope\\s*(you|she|he|they)\\s*dies?": ['report', True],
		 "(hang|neck) (him|her|them ?sel(f|ve)s?)": ['report', True],
		 "kill myself": ['report', True]}

checking = ('all') # 'submissions' = submissions, 'comments' = comments, 'all' = both comments and submissions
