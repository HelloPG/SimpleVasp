#!/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import logging

#from webapp2_extras import json
import json

from models.Models import Stock, UserStock

	
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
	

class MainHandler(webapp2.RequestHandler):

  def get(self):
    userName = ''
    ticker = token =  companyName = None
    us = []
    url_linktext = 'Login'
    url = users.create_login_url(self.request.uri)
     
    # Check any request parameters : /?ticker=""&token=""
    try:
      ticker = self.request.get("ticker")
      token = self.request.get("token")
      
      # check if request is for Public Valuation
      if (token != 'Public'):
        # Check if ticker is associated with username
        us = UserStock.query(UserStock.pseudoname == token, UserStock.ticker == ticker)
        
        if (us == []):
          ticker = None
        else: 
          companyName = us.get().companyName
        
      else:
        st = Stock.query(Stock.ticker == ticker).get()
        
        if (st != None):
          companyName = st.name
        
    except:
      user = users.get_current_user()
     
      if user:
        userName = user.nickname()
        # Get User Stocks
        url_linktext = 'Logout'
        url = users.create_logout_url(self.request.uri)   

        # Get user stocks 
        us = UserStock.query(UserStock.user == userName) 

    template_values = {
           'userName': userName,
           'userStocks': us,
           'ticker': ticker,
           'token': token,
           'companyName': companyName,
           'url': url,
           'url_linktext': url_linktext,
     }
    
    template = JINJA_ENVIRONMENT.get_template('home.html')
    self.response.write(template.render(template_values))
		

class AboutHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    userName = ''
    us = []
     
    if user:
     userName = user.nickname()
     # Get User Stocks
     url_linktext = 'Logout'
     url = users.create_logout_url(self.request.uri)   

     # Get user stocks 
     us = UserStock.query(UserStock.user == userName) 
                
     #for p in q.iter():
     # userStocks.append(p.ticker)

     
    else:
     url_linktext = 'Login'
     url = users.create_login_url(self.request.uri)

    template_values = {
           'userName': userName,
           'userStocks': us,
           'url': url,
           'url_linktext': url_linktext,
     }
     
    template = JINJA_ENVIRONMENT.get_template('about.html')
    self.response.write(template.render(template_values))	
        
json_data_file = open(os.path.join(os.path.dirname(__file__) + "/data", "ticker.json"))
json_data = json.load(json_data_file)

    
class StockTickerJsonHandler(webapp2.RequestHandler):
  def get(self):
    self.response.content_type = 'application/json'
    self.response.write(json.dumps(json_data))


# Admin Function: See user stats    
class UserStats(webapp2.RequestHandler):
  def get(self): 
    # Get total number of spreadsheets
    usCount = UserStock.query().count()
    
    # Get total number of users
    userCount = UserStock.query(projection=["user"], distinct=True).count()    
       
    # Show stats on console
    self.response.write("Number of Users = " + str(userCount) + "<br \>")
    self.response.write("Number of Spreadsheets = " + str(usCount) + "\n")
    




	
