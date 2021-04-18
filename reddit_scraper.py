"""
TODO: navigate to subreddit
TODO: iterate through each post filtering out the tags
TODO: iterate through each post and filter out the comments for cashtags
TODO: store the above in a table = store in database store as an object? 
TODO: sort by most mentioned
TODO: visualize in a graph
TODO: create a frontend table to display
"""

import json, sys, traceback, praw, sqlite3, logging
from datetime import date
import numpy as np
import pandas as pd
from yahoofinancials import YahooFinancials
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
            traceback.print_exc(file=sys.stdout)
            logger.error(e)

    # Looks for potential tickers from a block of text
    def tickerIdentifier(self, text):
        # Initialize SQL
        connection = sqlite3.connect('BrokeAz.db')
        cursor = connection.cursor()

        # Retrieve cashtag and allcap words with length 3-5 and remove any special characters
        try:
            potentialTickers = [
                word for word in text.split() if word.isupper() or "$" in word]
            potentialTickers = [''.join(e for e in word if e.isalnum())
                                for word in potentialTickers]
            potentialTickers = [
                word.upper() for word in potentialTickers if len(word) >= 3 and len(word) <= 5 and word.isalpha()]
        
        # Insertion Process: Add to Dictionary
            for ticker in potentialTickers:
                # Check if it is a Real Stock Symbol by checking the DB
                # if not in word_exclusion table proceed to cross check with YahooFinancials to ensure its a valid Ticker (Line 108-109)
                # if invalid YahooFinancials(ticker).get_stock_quote_type_data() will return { {Ticker} : None } (Line 111)
                # insert to dictionary otherwise insert capitalized word to DB if not a valid ticker  (Line 112/114)
                cursor.execute("SELECT word FROM word_exclusion where word='{}'".format(ticker.upper()))
                if cursor.fetchone() == None:
                    test = YahooFinancials(ticker).get_stock_quote_type_data()
                    for key, val in test.items():
                        if val != None:
                            self.tickers[ticker] = self.tickers.get(ticker, 0) + 1 
                        else:
                            cursor.execute("INSERT INTO word_exclusion (word) VALUES ('{}')".format(ticker.upper()))
                            connection.commit()
                else:
                # Skip to the next ticker
                    continue

            return self.tickers

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            logger.error(e)



if __name__ == '__main__':
    tickers = dict()

    logger.info("Reddit Scraper Starting...")
    scraper = SubredditScraper("day")

    logger.info("Beginning Insertion Process")
    logger.info("This May Take a Few Minutes...")
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

    # Connect to Database
    connection = sqlite3.connect('BrokeAz.db')
    cursor = connection.cursor()

    # Execute SQL Query
    today = date.today().isoformat()
    try:
        logger.info("Adding Dictionary to Database: scraped_stock")

        insertQuery = "INSERT INTO scraped_stocks (date, symbol, count) VALUES ('{}','{}',{})"
        updateQuery = "UPDATE scraped_stocks SET count={} WHERE date='{}', AND symbol='{}'"
        
        # Iterate through the dictionary
        for key, val in tickers.items():
            try:          
                # Insert into DB if doesn't exist
                logger.info(insertQuery.format(today, key, val))
                cursor.execute(insertQuery.format(today, key, val))
                connection.commit()          
            except Exception as e:
                logger.warning(e)
                 # Update the count if it does exist 
                logger.info(updateQuery.format(val, today, symbol))
                cursor.execute(updateQuery.format(val, today, symbol))
                connection.commit()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        logger.error(e)

    connection.close()

    # Extract occurrences higher than 5 and sort Dictionary in alphabetical order
    tickerDict = {key:val for key, val in tickers.items() if val >= 5}
    tickerDict = {key:val for key, val in sorted(tickerDict.items(), key=lambda item: item[1])}

    print(json.dumps(tickerDict, indent=4))

    # plot bar graph
    names = list(tickerDict.keys())
    values = list(tickerDict.values())

    plt.bar(range(len(tickerDict)), values, tick_label=names)
    plt.title("Reddit Stock Sentiment - {}".format(today))
    plt.ylabel("# of Mentions")
    plt.xlabel("Stock Ticker")
    plt.show()

