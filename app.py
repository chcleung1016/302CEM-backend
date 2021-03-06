# using flask_restful 
import tweepy
import pymysql
from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api 
import datetime
from datetime import date

# creating the flask app 
app = Flask(__name__) 

#setting the api
def start_api(consumer_key, consumer_secret,
  access_token, access_token_secret):

  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)  
  auth.set_access_token(access_token, access_token_secret)  
  return tweepy.API(auth)

#api authentication key
ck="DxHoukAprUS9cgUXR4yLPfy5n"
cs="2s1fiLCR4QGdlBVkDPh0WQgGOWA6rmcFIE5wzY5nYa1AsSayn2"
at="1207894049106956288-vVSh9pHeHm0GRKRXTNxnVVM9Ep1aiD"
ats="FY40u4cNBixTBzl5n9lH4847IGz5vCbHSBbYH9BNrK2g1"

my_api = start_api(ck,cs,at,ats)

#name = "Facebook"

@app.route('/<name>')
def get_user_info(api, name):
    
  user = api.get_user(screen_name = name) 
  return [user.name, user.created_at.strftime('%Y-%m-%d'),user.followers_count, user.friends_count,
    user.statuses_count, user.favourites_count]

print(get_user_info(my_api, name))

user, cre, followers, following, tweet, like = get_user_info(my_api, name)

#insert the data in the mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:P@ssw0rd123@127.0.0.1/twitter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Account_created(db.Model):
    __tablename__ = 'Account_created'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50))
    created_at = db.Column('created_at', db.DateTime)

    def __init__(self, username, created_at):
        self.username = username
        self.created_at = created_at


class Twitter(db.Model):
    __tablename__ = 'Twitter'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50))
    DATE = db.Column('DATE', db.Date)
    followers_count = db.Column('followers_count', db.Integer)
    following_count = db.Column('following_count', db.Integer)
    tweet_count = db.Column('tweet_count', db.Integer)
    like_count = db.Column('like_count', db.Integer)

    def __init__(self, username, DATE, followers_count, following_count, tweet_count, like_count):
        self.username = username
        self.DATE = DATE
        self.followers_count = followers_count
        self.following_count = following_count
        self.tweet_count = tweet_count
        self.like_count = like_count
        
def insert_data(name):
  
  today = date.today()
  exists = db.session.query(Account_created.id).filter_by(username=user).scalar() is not None
  dateexist = db.session.query(Twitter.id).filter_by(DATE = today, username = user).scalar() is not None
  print (exists);
  print(dateexist);

  if(exists == False):
   data = Account_created(user,cre)
   db.session.add(data)
   db.session.commit()

   insdata = Twitter(user,today.strftime('%Y-%m-%d'),followers,following,tweet,like)
   db.session.add(insdata)
   db.session.commit()
  elif(dateexist == False):
   insdata = Twitter(user,today.strftime('%Y-%m-%d'),followers,following,tweet,like)
   db.session.add(insdata)
   db.session.commit()
  elif(dateexist == True):
   updatedata = Twitter.query.filter_by(username = user, DATE = today).update({"followers_count": (followers), "following_count": (following), "tweet_count": (tweet), "like_count": (like)})
   db.session.commit()

  r = db.engine.execute('select username,DATE,followers_count,following_count,tweet_count,like_count from Twitter where username = "' + user + '" ORDER BY DATE DESC')

  x = [(a,b.strftime('%Y-%m-%d'),c,d,e,f) for (a,b,c,d,e,f) in r]

  y = [(x[i][2]-x[i-1][2],x[i][3]-x[i-1][3],x[i][4]-x[i-1][4])for i in range(len(x)-1)] + [(0,0,0)]

  z = [(x[i][0], x[i][1],
    x[i][2], y[i][0],
    x[i][3], y[i][1],
    x[i][4], y[i][2])
    for i in range(len(x))]

  print (z)

# make a new function here with a decorator implies an internal variable called "name"
@app.route('/<name>')
def flask_json(name):
    return insert_data(name)

# driver function 
if __name__ == '__main__':
    app.run(debug=True)
