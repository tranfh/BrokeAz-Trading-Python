"""
TODO: navigate to subreddit
TODO: iterate through each post filtering out the tags
TODO: iterate through each post and filter out the comments for cashtags
TODO: store the above in a table = store in database store as an object? 
TODO: sort by most mentioned
TODO: visualize in a graph
TODO: create a frontend table to display
"""
import sqlite3
import json
import praw
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import logging
import matplotlib.pyplot as plt

# create logger
logger = logging.getLogger('reddit_scrapper')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


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

    def __init__(self, searchRange):
        self.exclusions = [
            'ALL', 'AND', 'APPLE', 'ASK', 'BETA', 'BETS', 'BID', 'BIG', 
            'BILL', 'BMW', 'CBD', 'CEO', 'CFO', 'CTV', 'CHEAP', 'CLOSE', 'COVID', 
            'CURE', 'DFV', 'DOING', 'EDIT', 'ETF', 'EVERY', 'FAANG', 'FDA', 'FIX', 'FOMO', 
            'FTD', 'FUCK', 'GAS', 'GOING', 'GOOD', 'GRANT', 'HOLY', 'ICON', 
            'IMO', 'IOU', 'IPO', 'IRA', 'IRS', 'LARGE', 'LOOK', 'LOVE', 'MACD', 
            'MEDIA', 'META', 'MEETS', 'MOLY', 'MONEY', 'MOON', 'MORE', 'NASA', 
            'NEW', 'NEWS', 'NOT', 'ONCE', 'OTC', 'ONLY', 'PARKS', 'PENNY', 'PHIL', 
            'POP', 'PRICE', 'PUTS', 'QUICK', 'REIT', 'ROPE', 'RSI', 'SAFE', 
            'SAME', 'SEEK', 'SHARE', 'SHORT', 'STOCK', 'TAX', 'TLDR', 'THAN', 
            'THE', 'THEME', 'THREE', 'TTM', 'TSX', 'USD', 'WHERE', 'WSB', 'YEAR', 'YOLO', 'YOUR'
            ]

        self.posts: StockPost(postID, postURL, postTitle, postText, upvotes, comments) = []
        self.tickers = dict()
        # iterate through the posts and store them as an object
        try:
            logger.info("Gathering Reddit Posts from r/pennystocks, r/wallstreetbets, & r/stocks...")

            subs = ["pennystocks", "wallstreetbets", "stocks"]
            # Iterate through all posts of subreddits above for given range
            for sub in subs:
                for submission in reddit.subreddit(sub).top(searchRange):
                    try:
                        logger.info(str(submission.title))
                        post = StockPost(str(submission.id), str(submission.url), str(submission.title),
                                        str(submission.selftext), submission.score, submission.comments)
                        self.posts.append(post)
                    except Exception as e:
                        logger.warning(e)
                        continue
                
                logger.info("Number of Post Retrieved Today: " + str(len(self.posts)))

        except Exception as e:
            logger.error(e)

    # Looks for potential tickers from a string of text
    def tickerIdentifier(self, text):
        # retrieve cashtag and any capitalized words
        try:
        # retrieve cashtag and any capitalized words
            potentialTickers = [
                word for word in text.split() if word.isupper() or "$" in word]
        # remove any special characters
            potentialTickers = [''.join(e for e in word if e.isalnum())
                                for word in potentialTickers]
        # retrieve only 4 letter words
            potentialTickers = [
                word for word in potentialTickers if len(word) >= 3 and len(word) <= 5 and word.isalpha()]
        
        # add to dictionary
            for ticker in potentialTickers:
                print(ticker)
                if ticker not in self.exclusions:
                    self.tickers[ticker] = self.tickers.get(ticker, 0) + 1  

            return self.tickers

        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    tickers = dict()
    logger.info("Reddit Scraper Starting...")
    scraper = SubredditScraper("day")
    for redditPost in scraper.posts:
        postTitleTickers = scraper.tickerIdentifier(redditPost.postTitle)
        postTickers = scraper.tickerIdentifier(redditPost.postText)
        
        # merge dictionaries
        temp = {**postTickers, **postTitleTickers}
        tickers = {**tickers, **temp}

        # iterate through comments as well 
        # for comment in redditPost.comments:
        #     postComment = scraper.tickerIdentifier(comment.body)
        #     tickers = {**tickers, **postComment}

    # extract occurrences higher than 5 and sort Dictionary in alphabetical order
    tickerDict = {key:val for key, val in tickers.items() if val >= 5}
    tickerDict = {key:val for key, val in sorted(tickerDict.items(), key=lambda item: item[1])}

    print(json.dumps(tickerDict, indent=4))

    # plot bar graph
    names = list(tickerDict.keys())
    values = list(tickerDict.values())

    plt.bar(range(len(tickerDict)), values, tick_label=names)
    plt.show()

