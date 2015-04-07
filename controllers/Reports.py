#!/usr/bin/env python

import os
import urllib, cgi
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2, webapp2, webapp2, json, numpy, logging

from models.Models import Stock, UserStock, AnalystRating, EarningSurprise
from controllers import Common
	
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

    
class Top100Handler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    userName = ''
     
    if user:
      userName = user.nickname()

      url_linktext = 'Logout'
      url = users.create_logout_url(self.request.uri)   
      
    else:
      url_linktext = 'Login'
      url = users.create_login_url(self.request.uri)
      
    template_values = {
           'userName': userName,
           'url': url,
           'url_linktext': url_linktext,
     }
     
    template = JINJA_ENVIRONMENT.get_template('Top100.html')
    self.response.write(template.render(template_values))	


class topDataFetch(webapp2.RequestHandler):
  def post(self):
    self.response.headers['Content-Type'] = 'application/json'
    postDataDict = json.loads(cgi.escape(self.request.body))
    vt = postDataDict['vt']

    # Get Current Date - 10days
    cutoffDate = datetime.datetime.now() - datetime.timedelta(days = 10)

    # Get data for last 10 days
    if (vt=='UV'):
      q = Stock.query(Stock.ivPrem > 0, Stock.ivPrem < 2).order(Stock.ivPrem)
    elif (vt=='OV'):
      q = Stock.query(Stock.ivPrem < 0, Stock.ivPrem > -1).order(-Stock.ivPrem)

    data = []

    i = 0

    for p in q.iter():
      if (i > 99):
        break

      if (Common.xformNan(p.price) == '' or Common.xformNan(p.iValue) == ''):
        continue

      data.append({'ticker':p.ticker, 'name':p.name,
                   'price':p.price, 'iValue':p.iValue,
                   'ivPrem': p.ivPrem,
                   'peRatio': p.peRatio, 'pbRatio': p.pbRatio})
      i = i + 1

    # JSON data
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(
                                        {'data': data}
                                      )
                           )


#############################################################################


class AnalystRatingsHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    userName = ''

    if user:
      userName = user.nickname()

      url_linktext = 'Logout'
      url = users.create_logout_url(self.request.uri)

    else:
      url_linktext = 'Login'
      url = users.create_login_url(self.request.uri)

    template_values = {
           'userName': userName,
           'url': url,
           'url_linktext': url_linktext,
     }

    template = JINJA_ENVIRONMENT.get_template('analystRatings.html')
    self.response.write(template.render(template_values))

# Get Analyst ratings with valuations
class arDataFetch(webapp2.RequestHandler):
  def post(self):
    self.response.headers['Content-Type'] = 'application/json'
    postDataDict = json.loads(cgi.escape(self.request.body))
    vt = postDataDict['vt']
    rc = postDataDict['rc']

    # Get Current Date - 10days
    cutoffDate = datetime.datetime.now() - datetime.timedelta(days = 10)

    # Get data for last 10 days
    if (rc=='ALL'):
      q = AnalystRating.query(AnalystRating.date > cutoffDate).order(-AnalystRating.date)
    else:
      q = AnalystRating.query(AnalystRating.date > cutoffDate, AnalystRating.direction == rc).order(-AnalystRating.date)

    data = []
    i = 0
    
    for p in q.iter():
      ticker = p.ticker
      
      # Get other data from Stock
      st = Stock.query(Stock.ticker == ticker).get()

      if (st != None):
        if (vt=='UV'):
            if (st.iValue<st.price):
                continue
        elif (vt=='OV'):
            if (st.iValue>st.price):
                continue

        data.append({'date': str(p.date), 'ticker':ticker, 'name':st.name,
                     'analyst': p.analyst, 'oldRating': p.oldRating, 'newRating': p.newRating,
                     'ivPrem': Common.xformNan(st.ivPrem),
                     'peRatio': Common.xformNan(st.peRatio),
                     'pbRatio': Common.xformNan(st.pbRatio)
                   })

      
    # JSON data	
    self.response.headers['Content-Type'] = 'application/json'   
    self.response.out.write(json.dumps(
                                        {'data': data}
                                      )
                           )               


#############################################################################

class EarningSurprisesHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    userName = ''

    if user:
      userName = user.nickname()

      url_linktext = 'Logout'
      url = users.create_logout_url(self.request.uri)

    else:
      url_linktext = 'Login'
      url = users.create_login_url(self.request.uri)

    template_values = {
           'userName': userName,
           'url': url,
           'url_linktext': url_linktext,
     }

    template = JINJA_ENVIRONMENT.get_template('earningSurprises.html')
    self.response.write(template.render(template_values))


# Get Earning Surprises
class esDataFetch(webapp2.RequestHandler):
  def post(self):
    self.response.headers['Content-Type'] = 'application/json'
    postDataDict = json.loads(cgi.escape(self.request.body))
    vt = postDataDict['vt']
    st = postDataDict['st']

    # Get Current Date - 10days
    cutoffDate = datetime.datetime.now() - datetime.timedelta(days = 10)

    # Get data for last 10 days
    if (st=='ALL'):
      q = EarningSurprise.query(EarningSurprise.date > cutoffDate).order(-EarningSurprise.date)
    else:
      q = EarningSurprise.query(EarningSurprise.date > cutoffDate, EarningSurprise.direction == st).order(-EarningSurprise.date)

    data = []
    i = 0

    for p in q.iter():
      ticker = p.ticker
      logging.info("ticker=" + ticker)
      # Get other data from Stock
      st = Stock.query(Stock.ticker == ticker).get()

      if (st != None):
        if (vt=='UV'):
            if (st.iValue<st.price):
                continue
        elif (vt=='OV'):
            if (st.iValue>st.price):
                continue

        data.append({'date': str(p.date), 'ticker':ticker, 'name':st.name,
                     'estimate':Common.xformNan(p.estimate),
                     'actual':Common.xformNan(p.actual),
                     'percentSurprise': Common.xformNan(p.percentSurprise),
                     'ivPrem': Common.xformNan(st.ivPrem),
                     'peRatio': Common.xformNan(st.peRatio),
                     'pbRatio': Common.xformNan(st.pbRatio)
                   })


    # JSON data
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(
                                        {'data': data}
                                      )
                           )
