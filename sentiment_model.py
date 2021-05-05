# Purpose: To obtain corpus from twitter API, create engine for trading, and create portfolio. 

import tweepy
import pandas as pd
import re
import string

# For finance API call to extreact Bitcoin price.
import requests
import json

# For time calling of main function.
import threading

from textblob import TextBlob
from tweepy import OAuthHandler

import time

from datetime import datetime
from time import sleep

# keys and secrets to access twitter API and twitter account
consumer_key = "uOwAix39O8NL3ORVPUlE3ut79"
consumer_secret = "QEmkuyQIu0pgBRf8AstKvZzoZyE4coViodjDcdUD2YgdEkn0Fa"
access_token = "1364707423123030018-tFh3Wly3pKyQIYsGPztxsmWVRfRtXa"
access_token_secret = "IemqtlLKv3mIHIWwGd3cOzqdq5ZghXf30Yw8h6UIeuIIh"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

pd = pd.DataFrame(columns=('Tweets', 'Polarity', 'Subjectivity'))

# Absolute path of results.json file.
file_name = "/Users/brandonarchuleta/Desktop/MSProject/src/main_enginer/results.json"
portfolio_file = "/Users/brandonarchuleta/Desktop/MSProject/src/main_enginer/portfolio_value.json"


def CollectingTweets(query):
    public_tweets = []

    # Extract Tweet Object with the given query. Limit 180 per 15 minutes.
    for tweet in tweepy.Cursor(api.search, q="Bitcoin", rpp=1, result_type="recent", include_entities=True,
                               lang="en").items(180):
        public_tweets.append(tweet)

    # Lists to hold tweet text and then polarity and subjectivity measures from textblob.
    tw = []
    pl = []
    su = []
    pattern1 = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    pattern2 = re.compile('RT @:?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    for tweet in public_tweets:
        tweet.text = pattern1.sub('', tweet.text)
        tweet.text = pattern2.sub('', tweet.text)

        # Remove punctuations from the text
        tweet.text = "".join(i for i in tweet.text if i not in string.punctuation)

        # Reduce Extra spaces within the tweet
        tweet.text = re.sub("\s+", " ", tweet.text)

        # Normalize the case of the text
        tweet.text = "".join([i.lower() for i in tweet.text if i not in string.punctuation])

        str(tweet.text)
        sent = TextBlob(tweet.text)
        tw.append(tweet.text)
        pl.append(sent.sentiment.polarity)
        su.append(sent.sentiment.subjectivity)

    pd['Tweets'] = tw
    pd['Polarity'] = pl
    pd['Subjectivity'] = su
    return pd


def GetPolarityMean(pd):
    return pd['Polarity'].mean()

    return pd.count().Tweets


# Write json data to file. In this case, we will append each 15 minute call to the results.json file
# Output: Dictionary with engine data --> results.json

def write_data_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


portfolio_meta = {
    "original_investment": 100000,
    "principle": 100000,
    "net_gain_or_loss": 0,
    "current_value": 0,
    "coins_held": 0,
    "time": 0
}


def portfolio(portfolio_meta, bitcoin_data):
    if portfolio_meta["principle"] >= 0 and bitcoin_data["indication"] == "BUY":

        purchased_coins = portfolio_meta["principle"] / float(bitcoin_data["bitcoin_price"].replace(",", ""))
        portfolio_meta["principle"] = portfolio_meta["principle"] - (
                    purchased_coins * float(bitcoin_data["bitcoin_price"].replace(",", "")))
        portfolio_meta["coins_held"] += purchased_coins

        portfolio_meta["current_value"] = portfolio_meta["coins_held"] * float(
            bitcoin_data["bitcoin_price"].replace(",", ""))
        portfolio_meta["net_gain_or_loss"] = portfolio_meta["current_value"] - portfolio_meta["original_investment"]

        portfolio_meta["time"] = time.time()

    else:

        sold_coins = portfolio_meta["current_value"] / float(bitcoin_data["bitcoin_price"].replace(",", ""))
        portfolio_meta["principle"] += sold_coins * float(bitcoin_data["bitcoin_price"].replace(",", ""))
        portfolio_meta["coins_held"] -= sold_coins
        portfolio_meta["current_value"] = portfolio_meta["principle"]
        portfolio_meta["net_gain_or_loss"] = portfolio_meta["current_value"] - portfolio_meta["original_investment"]

        portfolio_meta["time"] = time.time()

    with open(portfolio_file) as json_file:
        data = json.load(json_file)

        temp = data["value"]

        # python object to be appended
        # Organize all data into json format to be written to file.
        y = portfolio_meta

        # appending data to emp_details
        temp.append(y)

    write_data_json(data, portfolio_file)


def main():
    list = CollectingTweets("Bitcoin")

    # Using the coindesk api to request bitcoin price in live time.
    r = requests.api.get("https://api.coindesk.com/v1/bpi/currentprice.json")

    # extract the current bitcoin price from the json object which is returned as a dict from the json method.
    bitcoin_price = (((r.json()["bpi"])["USD"])["rate"])

    time_of_price_extraction = ((r.json()["time"])["updated"])

    # Polarity is defined on a -1 to 1 basis.

    indication = ""
    sentiment_score = 0
    if GetPolarityMean(list) >= 0:
        indication = "BUY"
        sentiment_score = GetPolarityMean(list)
        print(sentiment_score)

    else:
        indication = "SELL"
        sentiment_score = GetPolarityMean(list)
        print(sentiment_score)

    sentiment_score = GetPolarityMean(list)

    with open(file_name) as json_file:
        data = json.load(json_file)

        temp = data["results"]

        # python object to be appended
        # Organize all data into json format to be written to file.
        y = {"bitcoin_price": bitcoin_price, "sentiment_score": sentiment_score, "indication": indication,
             "time_of_price_extraction": time_of_price_extraction, "list_tweets": []}

        # Note: if you want to record the tweets analyzed. This is a lot of data so I ommitted it for now.
        for tweet in list["Tweets"].to_list():
            y["list_tweets"].append(tweet)

        # appending data to emp_details
        temp.append(y)

    write_data_json(data, file_name)

    portfolio(portfolio_meta, y)


# run the code every n seconds.
def run_code_n():
    threading.Timer(900.0, run_code_n).start()
    main()


# run the code every n number of seconds. We will want this to be 15 minutes for twitter API call.
run_code_n()
