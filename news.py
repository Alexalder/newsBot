import tweepy
import urllib
import urllib2
import logging

#Local modules
import passwords
from database import Account

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#Telegram message body
BASE_URL = 'https://api.telegram.org/bot' + passwords.telegram_token + '/'

def send(msg, chat_id):
    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
        'chat_id': str(chat_id),
        'text': msg.encode('utf-8'),
        'parse_mode': 'Markdown',
        'disable_web_page_preview': 'true',
    })).read()
    log.info('send message:')
    log.info(resp)

def authenticate():
    auth = tweepy.OAuthHandler(passwords.consumer_key, passwords.consumer_secret)
    auth.set_access_token(passwords.access_key, passwords.access_secret)
    return tweepy.API(auth)

def parseTweet(tweet_id, api = None):
    if api is None:
        api = authenticate()
    return api.get_status(tweet_id, tweet_mode='extended')._json['full_text']

def handleBBC(tweet):
    pos = tweet.rfind('http')
    editedTweet = tweet[:pos]
    if editedTweet[-1] == '\n':
        i = -1
        while editedTweet[i]=='\n':
            i -= 1
        editedTweet = editedTweet[:i+1]
        if editedTweet[i]!=' ':
            editedTweet += ' '
    editedTweet += '[Link](' + tweet[pos:] + ')'
    send(editedTweet, -1001180515970)

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
        for _ in range (3): #3 attempts
            try:
                statuses = api.user_timeline(user_id = account.user_id, since_id = account.last_tweet_id)
            except:
                log.exception('Tweet id retrieval:')
                continue
            else: #Tweets retrieved
                log.info('Successfully retrieved tweet ids')
                break
        else: #All attempts failed
            break

        if statuses:
            statuses.reverse()
            for status in statuses:
                for _ in range (3):
                    try:
                        log.debug(status)
                        if account.user_id in telegram:
                            telegram[account.user_id](parseTweet(status.id, api))
                    except:
                        log.exception('Tweet parsing:')
                        continue
                    else:
                        account.last_tweet_id = status.id #Save the last tweet parsed
                        log.info('Successfully parsed tweet:')
                        log.info(status.id)
                        break
                else:
                    break #All attemps failed, stop any more parsing from the account
            account.put()


