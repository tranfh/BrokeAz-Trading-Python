""" 
TODO: navigate to subreddit
TODO: iterate through each post filtering out the tags
TODO: iterate through each post and filter out the comments for cashtags
TODO: store the above in a table 
TODO: sort by most mentioned
TODO: visualize in a graph
TODO: create a frontend table to display  
"""

import praw
import json
import sqlite3
import pandas as pd
from datetime import datetime

reddit = praw.Reddit(
    client_id="CYi9axqx8plAYw",
    client_secret="JvgQKleChxSLS3XbsahJ49XjxRywfg",
    user_agent="BrokeAzScraper",
    username="trandn",
    password="fhtran96"
)


class StockPost(object):
    def __init__(self, postID, postURL, postTitle, postText, upvotes, comments):
        self.postID = postID
        self.postURL = postURL
        self.postTitle = postTitle
        self.postText = postText
        self.upvotes = upvotes
        self.comments = comments


class SubredditScraper:
    # +wallstreetbets+stocks

    def __init__(self):
        self.posts = []
        self.tickers = dict()
        subreddit = reddit.subreddit("pennystocks")

        # iterate through the posts and store them as an object
        for submission in subreddit.top("day"):
            post = StockPost(submission.id, submission.url, submission.title,
                             submission.selftext, submission.score, submission.comments)
            self.posts.append(post)

    # Looks for potential tickers from a string of text
    def tickerIdentifier(self, text):
        # retrieve cashtag and any capitalized words
        potentialTickers = [
            word for word in text.split() if word.isupper() or "$" in word]
        # remove any special characters
        potentialTickers = [''.join(e for e in word if e.isalnum())
                            for word in potentialTickers]
        # retrieve only 4 letter words
        potentialTickers = [
            word for word in potentialTickers if len(word) == 4]

        # store them in a dictionary
        print("Storing in Dict")
        for ticker in potentialTickers:
            print(ticker)
            self.tickers[ticker] = self.tickers.get(ticker, 0) + 1

        print(json.dumps(self.tickers, indent=4))


s = SubredditScraper()
s.tickerIdentifier(s.posts[0].postText)
