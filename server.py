import json
import os

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
from tornado.ioloop import IOLoop
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import pandas as pd

import tweepy as tp
from tweepy import OAuthHandler

consumer_key = "" # API key
consumer_secret = "" # API secret
token = ""
token_secret = ""

#Write all functions in this class.
#Please use comments and necessary format like in example function.
#****EXAMPLE FUNCTION*****
#Function for searching tweets.
#Author: Recep Deniz Aksoy
def search_tweet(word):


    #Getting auth using consumer_token and consumer_secret as auth variable.
    auth = OAuthHandler(consumer_key, consumer_secret)
    api = tp.API(auth)
    #Using tp.Cursor function get 10 tweets which have bogazici in it.
    data = tp.Cursor(api.search, q= word, languages = 'tr', tweet_mode = 'extended').items(10)
    #Printing all 10 tweets.
    raw_table = []
    for tweet in data:
            raw_table.append(tweet._json['full_text'])
    table = pd.DataFrame.from_dict(raw_table)

    return table

#A function that collects trending topics for given location
#Author: Onur Varkıvanç
def trending_topics(wloc = 1):

    #Getting auth using consumer_token and consumer_secret as auth variable.
    auth = OAuthHandler(consumer_key, consumer_secret)
    api = tp.API(auth)

    #Get trending topics for the given location (default value is worldwide, 1)
    trends = api.trends_place(wloc)
    #Printing the names of the topics
    raw_table = []
    for trend in trends[0]['trends']:
        raw_table.append(trend['name']) #may require checking for unicode characters
    table = pd.DataFrame.from_dict(raw_table)
    return table

#Function for getting followers
#Author: Oğuzhan Yetimoğlu

def get_followers(word):

    auth = OAuthHandler(consumer_key, consumer_secret)
    api = tp.API(auth)
    raw_table = []
    data = tp.Cursor(api.followers, screen_name = word).items()
    for user in data:
        raw_table.append(user.screen_name)
    table = pd.DataFrame.from_dict(raw_table)
    return table

#Function for getting friends
#Author: Oğuzhan Yetimoğlu

def get_friends(word):

    auth = OAuthHandler(consumer_key, consumer_secret)
    api = tp.API(auth)
    raw_table = []
    data = tp.Cursor(api.friends, screen_name = word).items()
    for user in data:
        raw_table.append(user.screen_name)
    table = pd.DataFrame.from_dict(raw_table)
    return table

#Function for sending Direct Message
#Author: Ali Uslu

def send_direct_message(word, message):

    auth = tp.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(token, token_secret)
    api = tp.API(auth)
    api.send_direct_message(screen_name=word, text=message)

#Function for checking friendship
#Author: Ozge Dincsoy
def exist_friendship(user_A, user_B):
    auth = OAuthHandler(consumer_key, consumer_secret)
    api = tp.API(auth)
    user_friends_list = tp.Cursor(api.friends, screen_name = user_A).items()
    for friend in user_friends_list:
        if friend.screen_name == user_B.screen_name:
            return True
    return False

#Function for checking two sided following for a user
#Author: Ozge Dincsoy
def two_sided_following(user):
    auth = OAuthHandler(consumer_key, consumer_secret)
    api = tp.API(auth)
    two_sided_friendship = []
    user_friends_list = tp.Cursor(api.friends, screen_name = user).items()
    for friend in user_friends_list:
        is_following = exist_friendship(friend, user)
        if is_following :
            two_sided_friendship.append(friend.screen_name)
    table = pd.DataFrame.from_dict(two_sided_friendship)
    return table

#Function for getting users favorite tweets
#Author: Umutcan Uvut
def get_favs(username):
    auth = OAuthHandler(consumer_key, consumer_secret)
    api = tp.API(auth)
    data = api.favorites(id = username)
    # Printing all 10 tweets.
    raw_table = []
    for favs in data:
        raw_table.append(favs._json['text'])
    table = pd.DataFrame.from_dict(raw_table)
    return table

#Function to post a tweet specified by the API user.
#Author: Anıl Can Kara
def post_tweet(YourTweet):
 	#Four necessary information to authenticate a Twitter account.

 	#Handles the authentication by taking the consumer keys and access tokens as parameters.
    authentication = OAuthHandler(consumer_key, consumer_secret)
    #If the access token and the access key is not known, redirect the user to authenticate:

    #redirect_user(authentication.get_authorization_url())
    #auth.get_access_token("verifier_value")

    authentication.set_access_token(token, token_secret)

 	#Starts the API on that user instance specified above.
    api = tweepy.API(authentication)

	#Posts a tweet in that user's account.
    api.update_status(YourTweet)

#Function to follow back all the users following the authenticated user.
#Author: Anıl Can Kara
def follow_back_everybody():

    #Handles the authentication by taking the consumer keys and access tokens as parameters.
    authentication = OAuthHandler(consumer_key, consumer_secret)
    authentication.set_access_token(token, token_secret)

    #Starts the API on that user instance specified above
    api = tweepy.API(authentication)

    #Follow back every follower of that user.
    for every_follower in tweepy.Cursor(api.followers).items():
    	every_follower.follow()



class TemplateRendering:
    def render_template(self, template_name, variables={}):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_path = dir_path+"/templates"
        template_dirs = [ template_path ]

        env = Environment(
            loader = FileSystemLoader(template_dirs),
            auto_reload=True,
            autoescape=False
        )
        env.globals['S'] = '/static'

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)

        content = template.render(variables)

        return content

class resultHandler(tornado.web.RequestHandler, TemplateRendering):
    def post(self):
        method_type = self.get_argument('method_type')
        username = self.get_argument('username')
        word = self.get_argument('word')
        
        if(method_type == "search"):
            #Search word in val1 field.
            table = search_tweet(word)
            self.write(self.render_template('result.html', variables = {'result' : table.to_html(index = False)}))
        elif(method_type == "tt"):
            #If no location argument is passed to the function, it shows the worldwide results.
            table = trending_topics()
            self.write(self.render_template('result.html', variables = {'result' : table.to_html(index = False)}))
        elif(method_type == "searchFriends"):
            table = get_friends(username)
            self.write(self.render_template('result.html', variables = {'result' : table.to_html(index = False)}))

        elif(method_type == "searchFollowers"):
            table = get_followers(username)
            self.write(self.render_template('result.html', variables = {'result' : table.to_html(index = False)}))
        elif (method_type == "getFavs"):
            table = get_favs(username)
            self.write(self.render_template('result.html', variables={'result': table.to_html(index=False)}))
		
        elif (method_type == "twoSidedFriendship"):
            table = two_sided_following(username)
            self.write(self.render_template('result.html', variables={'result': table.to_html(index=False)}))

        elif(method_type == "sendDirectMessage"):
            send_direct_message(username, 'message')
        elif(method_type == "post_tweet"):
        	#Post the tweet typed into the YourTweet field.
            post_tweet(YourTweet);
        elif(method_type == "follow"):
        	follow_back_everybody();


class IndexPageHandler(tornado.web.RequestHandler, TemplateRendering):
    def get(self):

        self.write(self.render_template("index.html"))



class Application(tornado.web.Application):
    def __init__(self):

        handlers = [
            (r'/', IndexPageHandler),
            (r'/index.html', IndexPageHandler),
            (r'/result', resultHandler)
#            (r'/logs/(.*)',logsHandler),
#       (r'/reports/(.*)',tornado.web.StaticFileHandler,{'path':"./reports/"})
        ]

        settings = {
            'template_path': 'templates',
            'static_path': 'static'
        }
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    pd.set_option('display.max_colwidth', -1)
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(9090)
    tornado.ioloop.IOLoop.instance().start()
