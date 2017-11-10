import tweepy
import urllib
import urllib2
from google.appengine.ext import ndb

import passwords
BASE_URL = 'https://api.telegram.org/bot' + passwords.telegram_token + '/'

class Account(ndb.Model):
    user_id = ndb.IntegerProperty(required=True)
    last_tweet_id = ndb.IntegerProperty(indexed=False)
    
    def save(self, user, tweet_id):
        self.user_id = user
        last_tweet_id = tweet_id
        try:
            self.put()
            return True
        except Exception, e:
            return False

    def get(key):
        try:
            account = key.get()
            return account
        except:
            return None
                
    def delete(user):
        try:
            ndb.delete_multi(Account.query(Account.user_id == user))
            return True
        except Exception, e:
            return False

def send(msg, chat_id):
    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
        'chat_id': str(chat_id),
        'text': msg.encode('utf-8'),
        'disable_web_page_preview': 'true',
    })).read()

def newsHandler():
    telegram = {}
    telegram[5402612] = -1001180515970
    telegram[4252538955] = -1001226946977

    accounts = Account.query().fetch()
    auth = tweepy.OAuthHandler(passwords.consumer_key, passwords.consumer_secret)
    auth.set_access_token(passwords.access_key, passwords.access_secret)
    api = tweepy.API(auth)
    for account in accounts:
        statuses = api.user_timeline(user_id = account.user_id, since_id = account.last_tweet_id)
        if statuses:
            account.last_tweet_id = statuses[0].id
            account.put()
            statuses.reverse()
            for status in statuses: send(api.get_status(status.id,tweet_mode='extended')._json['full_text'],telegram[account.user_id])

def tweetGet(tweet_id, chat_id):
    auth = tweepy.OAuthHandler(passwords.consumer_key, passwords.consumer_secret)
    auth.set_access_token(passwords.access_key, passwords.access_secret)
    api = tweepy.API(auth)
    send(api.get_status(tweet_id, tweet_mode='extended')._json['full_text'], chat_id)

