import tweepy
import urllib
import urllib2

#Local modules
import passwords
from database import Account

#Telegram message body
BASE_URL = 'https://api.telegram.org/bot' + passwords.telegram_token + '/'

def send(msg, chat_id):
    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
        'chat_id': str(chat_id),
        'text': msg.encode('utf-8'),
        'disable_web_page_preview': 'true',
    })).read()

def authenticate():
    auth = tweepy.OAuthHandler(passwords.consumer_key, passwords.consumer_secret)
    auth.set_access_token(passwords.access_key, passwords.access_secret)
    return tweepy.API(auth)

def parseTweet(tweet_id, api = None):
    if api is None:
        api = authenticate()
    return api.get_status(tweet_id, tweet_mode='extended')._json['full_text']

def handleBBC(tweet):
    send(tweet, -1001180515970)

def handleNewsTg(tweet):
    editedTweet = tweet.replace('#ULTIMORA ', '')
    send (editedTweet, -1001226946977)

def handleMacRumors(tweet):
    send(tweet, -1001260217608)

def newsHandler():
    #Dictionary of Twitter id's and Telegram chat_id's
    telegram = {}
    telegram[5402612] = handleBBC #@BBCBreaking to 34ORE NEWS
    telegram[4252538955] = handleNewsTg #@NewsTG_ to 34ORE ITALIA
    telegram[14861285] = handleMacRumors #@MacRumors to 34ORE APPLE

    accounts = Account.getAllAccounts()
    api = authenticate()
    for account in accounts:
        statuses = api.user_timeline(user_id = account.user_id, since_id = account.last_tweet_id)
        if statuses:
            account.last_tweet_id = statuses[0].id #Save the last tweet parsed
            account.put()
            statuses.reverse()
            for status in statuses:
                if account.user_id in telegram:
                    telegram[account.user_id](parseTweet(status.id, api))




