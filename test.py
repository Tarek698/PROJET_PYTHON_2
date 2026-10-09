import os
import praw

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='WebScrapping'
)

try:
    for submission in reddit.subreddit("test").hot(limit=1):
        print(submission.title)
except Exception as e:
    print(f"Erreur : {e}")
