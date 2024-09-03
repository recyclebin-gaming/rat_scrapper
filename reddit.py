import praw

from bs4 import BeautifulSoup
import requests

import urllib.request
from json import dump
import hashlib
from os import makedirs


class RatsRetriever(praw.Reddit):
    def __init__(self):
        super().__init__("bot1", user_agent="user agent here")
        self._sub = self.subreddit("RATS")
        self.last_posts = []
        for submission in self._sub.hot(limit=10):
            self.last_posts.append(submission)

    @property
    def sub(self):
        self._sub.title
        return self._sub

    def get_hots(self, last: int = 10, limit: int = None):
        """returns all the new posts in the hot section since last time this method was called
        :param last: pull from the top x posts when comparing
        :param limit: return the top x new posts"""

        current_posts = []
        for submission in self.sub.hot(limit=last):
            current_posts.append(submission)

        new_posts = []
        for post in current_posts:
            if post not in self.last_posts:
                new_posts.append(post)

        self.last_posts = current_posts
        return new_posts[2:limit]

    @staticmethod
    def download_submissions(submission):
        if submission.is_video is True:
            try:
                urllib.request.urlretrieve(submission.secure_media['reddit_video']['fallback_url'],
                                       f"cache/{hash(submission)}.mp4")
            except FileNotFoundError:
                makedirs("cache")
                urllib.request.urlretrieve(submission.secure_media['reddit_video']['fallback_url'],
                                           f"cache/{hash(submission)}.mp4")

        elif submission.is_gallery is True:
            gallery_name = hashlib.md5(bytes(submission, "utf-8"))
            for media in submission.media_metadata:
                r = requests.get(submission.media_metadata[media]['p'][3]['u'])
                html = r.text
                page = BeautifulSoup(html, "html.parser")
                element = page.find("img")
                file_name = hash(element)
                urllib.request.urlretrieve(element["src"], f"cache/{gallery_name}_{file_name}.png")

                submission_data = {}
                submission_data.update({f"{gallery_name}_{file_name}.png": [submission.title, submission.url]})
                with open("db.json", "w") as file:
                    dump(submission_data, file)

        else:
            urllib.request.urlretrieve(submission.url, f"cache/{hash(submission)}.png")


if __name__ == "__main__":
    erm = RatsRetriever()
    submi = erm.submission('1ah0wzc')

