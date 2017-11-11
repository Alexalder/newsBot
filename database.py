from google.appengine.ext import ndb

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
