#!/usr/bin/python

# I'm not sure what I would change. I think everything is as efficient as possible, AFAIK.
# I've taken all of the constraints into account to minimize the size of the data structures,
# for example the filtering of the queries for 24hrs or younger.
#
# It would have been nice for the twitter api to support a "since" option that used a date,
# but it only supports twitter ID.
#
# I would have liked to have not had to make 4 passes over the data: 1 for ingest, 2 for processing,
# 1 for output


import os
import pickle
from datetime import datetime, timedelta

import tweepy


# we need to wrap many attributes in this logic because the values used for scoring must be
# retrieved from the original poster. if we retrieve the counts off of the base tweet rather
# then the retweeted_status, we'll end up scoring the tweet based on whoever joe shmoe is who
# retweeted it
def getRetweetableAttr(tweet, attribute):
    if hasattr(tweet, 'retweeted_status'):
        return reduce(getattr, attribute.split('.'), tweet.retweeted_status)
    else:
        return reduce(getattr, attribute.split('.'), tweet)


def getFollowersCount(tweet):
    return getRetweetableAttr(tweet, 'author.followers_count')


def getTweetId(tweet):
    return getRetweetableAttr(tweet, 'id')


def getRetweetCount(tweet):
    return getRetweetableAttr(tweet, 'retweet_count')


# a weighting factor based on how prolific of a followee you are
def generateScore(tweet):
    retweet_count = float(getRetweetCount(tweet))
    return float(getFollowersCount(tweet)) / float(max_followers) * 1 if retweet_count == 0 else retweet_count


# we only want tweets that are 24hrs or younger

def filterTweets(tweets):
    return [t for t in tweets if today - t.created_at <= timedelta(days=1)]


key = ''
secret = ''

client_token = ''
client_token_secret = ''

# Login as the user
auth = tweepy.OAuthHandler(key, secret)
auth.set_access_token(client_token, client_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
me = api.me()

# Lookup user's location
user_location = me.profile_location['id']  # twitter id
geo = api.geo_id(user_location)  # returns long, lat... very strange
clat = geo.centroid[1]  # lattitude
clong = geo.centroid[0]  # longitude

# finds WOEIDs where trends are happening near the user
woeids = [location['woeid'] for location in api.trends_closest(clat, clong)]

# retrieve trends. strange return structure though. There's a list with one entry, with a dict inside
# and I don't see how/why the list would ever be more than 1 entry long.
trends = [trend_data[0]['trends'] for trend_data in [api.trends_place(file_num) for file_num in woeids]]

articles = {}

max_followers = 0
max_retweets = 0
file_num = 0

today = datetime.today() + timedelta(hours=8)  # i believe the data is UTC

for trend in trends:
    for topic in trend:
        file_num += 1
        path = "cache/%d" % (file_num)

        # caching query results as I hit the API rate limit
        if not os.path.exists("cache"):
            os.mkdir("cache")
        if os.path.exists(path):
            file = open(path, 'r')

            tweets = filterTweets(pickle.load(file))
            file.close()
        else:
            tweets = filterTweets(api.search(q=topic['query']))
            file = open(path, 'w')
            pickle.dump(tweets, file)
            file.close()
        for tweet in tweets:
            if getTweetId(tweet) not in articles.keys():
                articles[getTweetId(tweet)] = {}
            articles[getTweetId(tweet)]['tweet'] = tweet
            if getFollowersCount(tweet) > max_followers:
                max_followers = getFollowersCount(tweet)
            if getRetweetCount(tweet) > max_retweets:
                max_retweets = getRetweetCount(tweet)

# generate a score for each tweet
for tweet in articles:
    articles[tweet]['score'] = generateScore(articles[tweet]['tweet'])

sorted_articles = sorted(articles.values(), key=lambda x: x['score'], reverse=True)

for tweet in sorted_articles[0:999]:
    print "http://twitter.com/statuses/%d, score: %f, retweet: %d, author.followers_count: %d" % (
        getTweetId(tweet['tweet']), tweet['score'],
        getRetweetCount(tweet['tweet']),
        getFollowersCount(tweet[
                              'tweet']))
