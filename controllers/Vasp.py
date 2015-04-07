#!/usr/bin/env python

import os
import urllib, cgi
import hashlib

import webapp2, logging, json, numpy

#from webapp2_extras import json

from google.appengine.api import users
from google.appengine.ext import ndb

#from models import Models
from models.Models import MarketData, Stock, UserStock, UserStockForecast, YearlyFinancial, CrowdStockForecast, AnalystEstimate

from controllers import Common

def getResultData(terminalFcfe, sumFcfe, nbrOfShares, iValue, price):
  resultData = []

  # Create JSON object for - Result
  resultData.append( {"id":"1", "rowName":"<b>Value on year 6 of next 15 years of FCFs<sup>1</sup></b>", "formula":"FCF<sub>5</sub>&times;[1-(1+COE)<sup>-15</sup>]&divide;COE", "value":terminalFcfe} )			
  resultData.append( {"id":"2", "rowName":"<b>Sum of all future  Discounted FCFs<sup>2</sup></b>", "formula":" 	&#931;( FCF<sub>n</sub>/(1+COE)<sup>n</sup> )", "value":sumFcfe} )			
  resultData.append( {"id":"3", "rowName":"<b>Number of Shares", "formula":"in millions</b>", "value":nbrOfShares} )		
  resultData.append( {"id":"", "rowName":"", "formula":"", "value":""} )	
  resultData.append( {"id":"", "rowName":"<b>Share Intrinsic Value (iValue)</b>", "formula":"Sum of all future  Discounted FCFs(2)<br />&divide;<br />Number of Shares(3)", "value":iValue} )		
  resultData.append( {"id":"", "rowName":"<b>Share Market Value</b>", "formula":"", "value":price} )		

  return resultData
     
class LoadAnalystEstimate(webapp2.RequestHandler):
       
  def post(self):
     postDataDict = json.loads(cgi.escape(self.request.body))
     ticker = postDataDict['ticker']     
     userName =  ''

     # If ticker is not specified, return error
     if (ticker == None or ticker.strip() == ''):
       self.response.headers['Content-Type'] = 'application/json'  
       self.response.out.write(json.dumps( {"errMessage": "Ticker not specified."} ) )
       return
       
     # Check for active Google account session
     user = users.get_current_user()
       
     # If user is not signed in, return error
     if (user == None):
       self.response.headers['Content-Type'] = 'application/json'  
       self.response.out.write(json.dumps( {"errMessage": "User not signed in."} ) )
       return

     # Get Analyst Estimates for the given ticker
     q = AnalystEstimate.query(AnalystEstimate.ticker == ticker, 
                               AnalystEstimate.year >= Common.CURRENT_YEAR,
                               AnalystEstimate.year < (Common.CURRENT_YEAR + Common.SHOW_PERIODS)
                              ).order(AnalystEstimate.year)

     # Create Json list for all the year - ni list
     aeJsonList = []
     
     for p in q.iter():
       aeJson = {}
       aeJson['year'] = p.year
       aeJson['ni'] = p.ni
       aeJsonList.append(aeJson)

     # Return analyst estimate JSON data	
     self.response.headers['Content-Type'] = 'application/json'   
     self.response.out.write(json.dumps(
                                         {'aeJsonList': aeJsonList}
                                       )
                            )       
       
       
       
class LoadFCFHandler(webapp2.RequestHandler):
       
  def post(self):
     postDataDict = json.loads(cgi.escape(self.request.body))
     ticker = postDataDict['ticker']
     token = postDataDict['token'].strip()
     userFlag = postDataDict['userFlag']      
     userName =  ''
     publicUrl = ''

     # If 'token' is specified, request came from 'publishValuation'
     if (token != ''):
     
       # Check if request came for Public 'publishValuation'
       if (token == 'Public'):
         userFlag = 'N'
       
       else:
         # Get userName from token
         us = UserStock.query(UserStock.pseudoname == token, UserStock.ticker == ticker).get()
         
         if (us == None):
           self.response.headers['Content-Type'] = 'application/json'  
           self.response.out.write(json.dumps( {"errMessage": "User valuation not found."} ) )
           return
         else: 
           userName = us.user
           userFlag == 'Y'
     
     else:
       token = 'Public'
       
       # Check for active Google account session
       user = users.get_current_user()
         
       # Check if current request is for 'User Estimates'
       # If user is not signed in, return error
       if (userFlag == 'Y' and user == None):
         self.response.headers['Content-Type'] = 'application/json'  
         self.response.out.write(json.dumps( {"errMessage": "User not signed in."} ) )
         return
         
       if (user != None):
         userName = user.nickname()   

         # If data fetched is user specific 
         if (userFlag == 'Y'):
           token = hashlib.sha1(userName).hexdigest()

     fcfDataPast = Common.getPastData(ticker)
     
     # If last sales value is not defined, return error
     if (fcfDataPast[0,0] == 0 or fcfDataPast[0,0]==None):
       self.response.headers['Content-Type'] = 'application/json'  
       self.response.out.write(json.dumps( {"errMessage": 
                                               "<p>Sorry, 'TheVasp' does not cover this stock.</p>" + 
                                               "<p>Either the stock is from finance industry <br />or<br /> Data is not available for the stock.</p>"
                                         } ) )
       return
       
     fcfDataForecast = Common.getForecastData(ticker, userFlag, userName)
     fcfData = []
   
    # Create JSON object
     fcfData.append(Common.getFcfRecord(1, "<b>Sales</b>", 0, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord("", "YrOverYr % Growth", 1, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord(2, "<b>Net Income</b>", 2, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord("", "As % of Sales", 3, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord(3, "<b>Depreciation</b>", 4, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord("", "As % of Sales", 5, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord(4, "<b>Deferred Taxes</b>", 6, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord("", "As % of Sales", 7, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord(5, "<b>Other Funds</b>", 8, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord("", "As % of Sales", 9, fcfDataPast, fcfDataForecast, userFlag))     
     fcfData.append(Common.getFcfRecord(6, "<b>Capital Expenditure</b>", 10, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord("", "As % of Sales", 11, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord(7, "<b>Working Capital Increase</b>", 12, fcfDataPast, fcfDataForecast, userFlag))
     fcfData.append(Common.getFcfRecord("", "As % of Sales", 13, fcfDataPast, fcfDataForecast, userFlag))

     fcfData.append( {"id":"", "rowName":"", "n5_":"", "n4_":"", "n3_":"", "n2_":"", "n1_":"", 
                      "PastAvg":"", "n1":"", "n2":"", "n3":"", "n4":"", "n5":"", "FM":"" } )			
     fcfData.append(Common.getFcfRecord("", "<b>FCFE (2+3+4+5-6-7)</b>", 14, fcfDataPast, fcfDataForecast, userFlag))
  
     ####################################  End of HandsOnTable data create ############################## 
     #logging.info(fcfData)
     
     publicUrlHtml = "<B>URL to publish this valuation:</B>&nbsp;&nbsp;" +  \
                     "<U>" + self.request.host_url + "/?token=" + token + "&ticker=" + ticker + "</U>" 
                       
     self.response.headers['Content-Type'] = 'application/json'   
     self.response.out.write(json.dumps({'fcfData': fcfData, 'userName': userName, 'publicUrlHtml': publicUrlHtml},
                                         allow_nan=True))
     
		

class LoadCOEHandler(webapp2.RequestHandler):
  def post(self):
     postDataDict = json.loads(cgi.escape(self.request.body))
     ticker = postDataDict['ticker']

     coeData = []
     resultData = []

     # Get latest Market Data
     q = MarketData.query().order(MarketData.entry_date).get()
     rf = q.Treasury10yrReturn
     rm = q.SP500Return
     
     # Get Stock Beta
     q = Stock.query(Stock.ticker == ticker).get()
     
     if (q == None):
       beta = None
       nbrOfShares = None
       price = None
     else:
       beta = q.beta
       nbrOfShares = q.shares_os
       price = q.price

     if (beta == None):
       beta = 'NA'

     if (nbrOfShares == None):
       nbrOfShares = 'NA'

     if (price == None):
       price = 'NA'
       
     # Calculate cost of Equity    
     if (beta == 'NA'):
       coe = rf + ( 1 * (rm - rf) )
     else:  
       coe = rf + ( float(beta) * (rm - rf) )
     
     coe = round(coe, 2)
     
     # Create JSON object for - COE
     coeData.append( {"id":"1", "rowName":"<b>r<sub>f</sub> = 10 year treasury yield</b>", "proxy":rf} )			
     coeData.append( {"id":"2", "rowName":"<b>&#946;<sub>a</sub> (Beta)<sup>*</sup></b>", "proxy":beta} )			
     coeData.append( {"id":"3", "rowName":"<b>r<sub>m</sub> = S&P 500, 1 year return</b>", "proxy":rm} )			
     coeData.append( {"id":"", "rowName":"", "proxy":""} )			
     coeData.append( {"id":"", "rowName":"<b>r<sub>a</sub> = Cost of Equity</b>", "proxy":coe} )			     

     # Create JSON object for - Result
     resultData = getResultData("", "", nbrOfShares, "", price)
     
     # Return ticker JSON data	
     self.response.headers['Content-Type'] = 'application/json'   
     self.response.out.write(json.dumps(
                                         {'coeData': coeData,
                                          'resultData': resultData
                                         }
                                       )
                            )

# Load Valuation Result Data from database
class LoadResultHandler(webapp2.RequestHandler):
  def post(self):
     self.response.headers['Content-Type'] = 'application/json' 
     postDataDict = json.loads(cgi.escape(self.request.body))              
     ticker = postDataDict['ticker']
     userFlag = postDataDict['userFlag']
     token = postDataDict['token']
     resultData = []
     
     if (token != ''):
       if (token == 'Public'):
         userFlag = 'N'
       else:
         userFlag = 'Y'
         
     st = Stock.query(Stock.ticker==ticker).get()
     
     # If ticker not found, return empty
     if (st != None):
       nbrOfShares = st.shares_os
       price = st.price
     
       # Crowd Valuation
       if (userFlag == 'N'):
         resultData = getResultData(st.terminalFcfe, st.fcfSum, nbrOfShares, st.iValue, price)
     
       # Individual Valuation
       else:
         # Check if the request is coming from published url
         if (token != ''):
           us = UserStock.query(UserStock.pseudoname==token, UserStock.ticker==ticker).get()
           
           if (us != None):
             resultData = getResultData(us.terminalFcfe, us.fcfSum, nbrOfShares, us.iValue, price)
 
         # Else get current user
         else:
           user = users.get_current_user()
         
           if (user != None):
             userName = user.nickname()
             us = UserStock.query(UserStock.user==userName, UserStock.ticker==ticker).get()
             
             if (us != None):
               resultData = getResultData(us.terminalFcfe, us.fcfSum, nbrOfShares, us.iValue, price)
       
     if (resultData == []):
       resultData = getResultData(None, None, nbrOfShares, None, price)
       
     self.response.out.write(json.dumps({'resultData': resultData}))
     
# Load Comparison Data for related companies
class LoadCompareHandler(webapp2.RequestHandler):
  def post(self):
    self.response.headers['Content-Type'] = 'application/json' 
    postDataDict = json.loads(cgi.escape(self.request.body))              
    ticker = postDataDict['ticker']
    userFlag = postDataDict['userFlag']
    token = postDataDict['token']
    compareData = []
    userName = None
    
    # Check if the request is coming from published url
    if (token != ''):
      if (token == 'Public'):
        userFlag = 'N'
      else:
        userFlag = 'Y'
    
    elif (userFlag == 'Y'):
      user = users.get_current_user()
        
      if (user == None):
        self.response.out.write(json.dumps({'compareData': compareData}))
        return
      else:
        userName = user.nickname()
        
    st = Stock.query(Stock.ticker==ticker).get()
    
    # If ticker not found, return empty
    if (st == None):
      self.response.out.write(json.dumps({'compareData': compareData}))
      return
      
    else:
      related = st.related
      
      if (related == None or related.strip() == ''):
        self.response.out.write(json.dumps({'compareData': compareData}))
        return
      
      # Get Stock records for the related stocks
      relList = related.split(',')
      q = Stock.query(Stock.ticker.IN(relList))
      
      for p in q.iter():  
        price = Common.getRound(p.price, 2)
        iValue = Common.getRound(p.iValue, 2)
        ivPrem = Common.getRound(p.ivPrem, 2)
        peRatio = Common.getRound(p.peRatio, 2)
        pbRatio = Common.getRound(p.pbRatio, 2)

        compareData.append({'ticker':p.ticker, 'name': p.name, 
                            'iValue': iValue, 'price': price,
                            'ivPrem': ivPrem,
                            'pbRatio': pbRatio,
                            'peRatio': peRatio})
      
      # If userFlag is 'Y', update iValue and pvRatio based on UserStock values
      if (userFlag == 'Y'):
        # If this is coming from Published URL
        if (token != ''):
          q = UserStock.query(UserStock.pseudoname==token, Stock.ticker.IN(relList))
        elif (userName != None):
          q = UserStock.query(UserStock.user==userName, Stock.ticker.IN(relList))
          
        for p in q.iter():  
          ticker = p.ticker
          iValue = p.iValue
          ivPrem = None
          
          # Find corresponding record in 'compareData'
          for cd in compareData:
            if (cd['ticker'] == ticker):
              cd['iValue'] = iValue
              price = cd['price']

              if (price != None and iValue != None and price > 0):
                cd['ivPrem'] = round((iValue - price)/price, 2)
              
      self.response.out.write(json.dumps({'compareData': compareData}))
     
     
# Input: List of future FCFs, COE, number of shares
# Output: Result: Terminal Value, Sum of all future discounted FCFs, Intrinsic value
class EvalResultHandler(webapp2.RequestHandler):
  def post(self):
     self.response.headers['Content-Type'] = 'application/json' 
     postDataDict = json.loads(cgi.escape(self.request.body))              
     coe = Common.parseFloat(postDataDict['coe'])
     nbrOfShares = Common.parseFloat(postDataDict['nbrOfShares'])
     price = Common.parseFloat(postDataDict['price'])
     fcfListParam = postDataDict['fcfList']
     fcfList = []
     resultData = []
     
     for i in range(0, Common.SHOW_PERIODS):  
       fcf = Common.parseFloat(fcfListParam[i])

       if (fcf == None or fcf == 0):  
         resultData = getResultData("", "", nbrOfShares, "", "")
         self.response.out.write(json.dumps({'resultData': resultData}))
         return
       else:
         fcfList.append(fcf)

     divBase = 1 + (coe/100); 
     div = dfcfe = dfcfeTotal = 0
     
     # Add terminal FCFE to the list   
     div = pow(divBase, 0 - Common.COMPANY_LIFE);
     terminalFcfe = round(fcfList[Common.SHOW_PERIODS-1] * (1 - div) / (coe/100))
     fcfList.append(terminalFcfe)
     
     for i in range(0, Common.SHOW_PERIODS+1):
       div = pow(divBase, i+1);
       dfcfe = round((fcfList[i] / div));
       dfcfeTotal = dfcfeTotal + dfcfe;

     # Calculate intrinsic value
     iValue = None
     if (nbrOfShares != 0):
       iValue = round(dfcfeTotal/nbrOfShares, 2)
        
     resultData = getResultData(terminalFcfe, dfcfeTotal, nbrOfShares, iValue, price)
     self.response.out.write(json.dumps({'resultData': resultData}))

	
class SaveVasp(webapp2.RequestHandler):
    def post(self):
        # Checks for active Google account session
        user = users.get_current_user()

        # If user is not signed in, return error
        if user is None:
            self.response.headers['Content-Type'] = 'application/json'  
            self.response.out.write(json.dumps( {"errMessage": "User not signed in."} ) )
		
        userName = user.nickname()
        
        postDataDict = json.loads(cgi.escape(self.request.body))
        
        dataFCF = []
        dataFCF = postDataDict['dataFCF']
        
        # Get stock ticker and Company Name
        tickerVal = postDataDict['ticker']
        companyNameVal = postDataDict['companyName']
        
        # If stock ticker is not specified, return error
        if tickerVal is None:
            self.response.headers['Content-Type'] = 'application/json'  
            self.response.out.write(json.dumps( {"errMessage": "Stock symbol not provided."} ) )
        
        # Check if stock ticker is present in 'UserStock'
        q = UserStock.query(UserStock.user == userName, UserStock.ticker == tickerVal)
        
        # If not, add it
        if (q.count() == 0):
            us = UserStock(user=userName, ticker=tickerVal, companyName=companyNameVal)
            # Get hash value for userid
            us.pseudoname = hashlib.sha1(userName).hexdigest()
            us.put()
        
        # Add/Update data for all the 5 years in 'UserStockForecast'
        fcfList = []
        for i in range(0, Common.SHOW_PERIODS):
       
          #Check if record already exists 
          usf = UserStockForecast.query(UserStockForecast.user == userName,
                                        UserStockForecast.ticker == tickerVal,        
                                        UserStockForecast.year == (Common.CURRENT_YEAR + i)).get() 

          # If not, create it
          if (usf == None):
            usf =  UserStockForecast(user=userName, 
                                     ticker=tickerVal, 
                                     year=(Common.CURRENT_YEAR + i))
            usf.put()

          #Update FCF values
          if (dataFCF[0]['n' + str(i+1)] != ''):
            usf.sales = dataFCF[0]['n' + str(i+1)]
          if (dataFCF[1]['n' + str(i+1)] != ''):
            usf.salesGrowth = dataFCF[1]['n' + str(i+1)]
          if (dataFCF[2]['n' + str(i+1)] != ''):
            usf.ni = dataFCF[2]['n' + str(i+1)]
          if (dataFCF[3]['n' + str(i+1)] != ''):
            usf.niPerSales = dataFCF[3]['n' + str(i+1)]         
          if (dataFCF[4]['n' + str(i+1)] != ''):
            usf.dep = dataFCF[4]['n' + str(i+1)]
          if (dataFCF[5]['n' + str(i+1)] != ''):
            usf.depPerSales = dataFCF[5]['n' + str(i+1)]
          if (dataFCF[6]['n' + str(i+1)] != ''):
            usf.defTaxes = dataFCF[6]['n' + str(i+1)]
          if (dataFCF[7]['n' + str(i+1)] != ''):
            usf.defTaxesPerSales = dataFCF[7]['n' + str(i+1)]
          if (dataFCF[8]['n' + str(i+1)] != ''):
            usf.other = dataFCF[8]['n' + str(i+1)]
          if (dataFCF[9]['n' + str(i+1)] != ''):
            usf.otherPerSales = dataFCF[9]['n' + str(i+1)]            
          if (dataFCF[10]['n' + str(i+1)] != ''):
            usf.capEx = dataFCF[10]['n' + str(i+1)]
          if (dataFCF[11]['n' + str(i+1)] != ''):
            usf.capExPerSales = dataFCF[11]['n' + str(i+1)]
          if (dataFCF[12]['n' + str(i+1)] != ''):
            usf.wcDelta = dataFCF[12]['n' + str(i+1)]
          if (dataFCF[13]['n' + str(i+1)] != ''):
            usf.wcDeltaPerSales = dataFCF[13]['n' + str(i+1)]
          
          if (dataFCF[15]['n' + str(i+1)] != ''):
            usf.fcf = dataFCF[15]['n' + str(i+1)]
            fcfList.append(usf.fcf)
            
          usf.put()
        
        # If all the FCFs are populated, Calculate Valuation Result
        if (len(fcfList) == Common.SHOW_PERIODS):
          stockRecord = Stock.query(Stock.ticker==tickerVal).get()
          
          if (stockRecord != None):
            coe = stockRecord.coe
            nbrOfShares = stockRecord.shares_os
            
            divBase = 1 + (coe/100); 
            div = dfcfe = dfcfeTotal = 0
            
            # Add terminal FCFE to the list   
            div = pow(divBase, 0 - Common.COMPANY_LIFE);
            terminalFcfe = round(fcfList[Common.SHOW_PERIODS-1] * (1 - div) / (coe/100))
            fcfList.append(terminalFcfe)
            
            for i in range(0, Common.SHOW_PERIODS+1):
              div = pow(divBase, i+1);
              dfcfe = round((fcfList[i] / div));
              dfcfeTotal = dfcfeTotal + dfcfe;
              dfcfeTotal = round(dfcfeTotal, 2)

            # Calculate intrinsic value
            iValue = None
            if (nbrOfShares != 0):
              iValue = round(dfcfeTotal/nbrOfShares, 2)
              
            # Save UserStock
            us = UserStock.query(UserStock.ticker == tickerVal, UserStock.user == userName).get()
            
            if (us != None):
              us.terminalFcfe = terminalFcfe
              us.fcfSum = dfcfeTotal
              us.iValue = iValue
              us.put() 
              
          
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps( {"result": "ok"} ) )
