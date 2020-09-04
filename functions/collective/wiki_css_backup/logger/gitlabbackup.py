from prawcore import RequestException, ResponseException, InvalidToken
import multiprocessing
import datetime
import gitlab
import config
import praw
import time
import sys
import os


class backup:
    def __init__(self):
        self.gl = gitlab.Gitlab(config.url, private_token=config.private_token)
        self.project = self.gl.projects.get(config.project_id)

        self.path = os.path.dirname(os.path.abspath(__file__))

        self.reddit = praw.Reddit(username=config.username,
                                  password=config.password,
                                  client_id=config.client_id,
                                  client_secret=config.secret,
                                  user_agent=config.user_agent)
        self.subreddit = self.reddit.subreddit(config.sub)

    def exc(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except InvalidToken:
                print("Encountered Invalid Token error, resetting PRAW")
                sys.exit()

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

        return wrapper

    @exc
    def save_wiki(self, moderator="NaN"):
        items = [file['path'] for file in self.project.repository_tree(path="wiki")]
        for n in range(10):
            for i in items.copy():
                if "." not in i:
                    items.pop(items.index(i))
                    [items.append(file['path']) for file in self.project.repository_tree(path=i)]

        saved_type = "wiki"
        action_list = list()

        for page in self.subreddit.wiki:
            page_name = str(page)[10:]
            new_action = dict()
            if "wiki/" + page_name + ".md" not in items:
                commit_action = "create"
            else:
                commit_action = "update"

            new_action.update({
                "action": commit_action,
                "file_path": "wiki/{}.md".format(page_name),
                "content": self.subreddit.wiki[page_name].content_md
            })

            action_list.append(new_action)

        data = {
            'branch': 'master',
            'commit_message': '{} | {} | {}'.format(saved_type, moderator, datetime.datetime.now().strftime(
                '%B %d, %Y at %I:%M:%S %p %Z')),
            'actions': action_list
        }

        self.project.commits.create(data)

    @exc
    def update_wiki(self, changed_file):
        wiki_target = changed_file[5:]
        wiki_target = wiki_target[:-3]

        # get file difference
        new_content = self.project.files.get(file_path=changed_file, ref='master').decode().decode("utf8")

        # write to wiki on the right page
        self.subreddit.wiki[wiki_target].edit(content=new_content, reason="Wiki update via Gitlab")

    @exc
    def save_css(self, moderator="NaN"):
        items = [file['path'] for file in self.project.repository_tree(path="css")]
        saved_type = "css"
        action_list = list()

        if "css/stylesheet.css" not in items:
            commit_action = "create"
        else:
            commit_action = "update"

        data = {
            'branch': 'master',
            'commit_message':
                f"{saved_type} | {moderator} | {datetime.datetime.now().strftime('%B %d, %Y at %I:%M:%S %p %Z')}",
            'actions': [
                {
                    "action": commit_action,
                    "file_path": "css/stylesheet.css",
                    "content": self.subreddit.stylesheet().stylesheet
                }
            ]
        }

        self.project.commits.create(data)

    @exc
    def update_css(self, changed_file="css/stylesheet.css"):
        # get file difference
        new_content = self.project.files.get(file_path=changed_file, ref='master').decode().decode("utf8")

        # write to stylesheet
        self.subreddit.stylesheet.update(new_content, reason="CSS update via Gitlab")

    @exc
    def modlog_css(self):
        while True:
            for log in self.subreddit.mod.stream.log(action="community_styling", skip_existing=True):
                self.save_css(moderator=str(log.mod))

    @exc
    def modlog_wiki(self):
        while True:
            for log in self.subreddit.mod.stream.log(action="wikirevise", skip_existing=True):
                self.save_wiki(moderator=str(log.mod))

    @exc
    def gitlab_edits(self):
        for commit in self.project.commits.list(ref_name='master'):
            new_latest_id = commit.get_id()
            break

        while True:
            try:
                latest_id = new_latest_id
                for commit in self.project.commits.list(ref_name='master'):
                    if commit.get_id() == latest_id:
                        break
                    else:
                        new_latest_id = commit.get_id()

                        if commit.title[:7] != "wiki | " and commit.title[:6] != "css | ":
                            for path_changed in range(len(commit.diff())):
                                if not commit.diff()[path_changed]['deleted_file']:
                                    if commit.diff()[path_changed]['new_path'] == "css/stylesheet.css":
                                        self.update_css(changed_file=commit.diff()[path_changed]['new_path'])
                                    elif commit.diff()[path_changed]['new_path'][:7] == "logger/":
                                        pass
                                    else:
                                        self.update_wiki(changed_file=commit.diff()[path_changed]['new_path'])

                time.sleep(30)

            except Exception as e:
                print(e)

    def processing(self):
        subprocess1 = multiprocessing.Process(target=self.modlog_css)
        subprocess2 = multiprocessing.Process(target=self.modlog_wiki)
        subprocess3 = multiprocessing.Process(target=self.gitlab_edits)

        subprocess1.start()
        subprocess2.start()
        subprocess3.start()


if __name__ == '__main__':
    backup().processing()
