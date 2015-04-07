#!/usr/bin/env python

import os
import csv

from google.appengine.ext import ndb
from google.appengine.api import taskqueue

import webapp2, logging, numpy, math


#from models import Models
from models.Models import Stock, UserStockForecast, YearlyFinancial, CrowdStockForecast, AnalystEstimate

from controllers import Common


    
# In the beginning, no user estimates will be present.
# Use past 5 year avg to calculate next 5 years numbers
class TheVaspAvgForecast(webapp2.RequestHandler):
  def get(self):   
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return
      
    # Less Than and Greater Than or Equal To characters
    # Used to split big jobs. A to ZZZZZZZZZZZZ
    # lt='M', gte='M'
    lt = self.request.get("lt")
    if (lt == None or lt == ''):
      lt = 'ZZZZZZZZZZZZ'
      
    gte = self.request.get("gte")
    if (gte == None or gte == ''):
      gte = 'A'    

    # Get List of Tickers from table - Stock    
    stocks = Stock.query(Stock.exchange == exchange,
                         Stock.ticker < lt,
                         Stock.ticker >= gte)
    
    # For each stock ticker     
    for stock in stocks.iter():
      taskqueue.add(url='/admin/TheVaspAvgForecastForStock', 
                    params={'ticker': stock.ticker} )
    
    self.response.out.write("TheVaspAvgForecast complete.")
    

class TheVaspAvgForecastForStock(webapp2.RequestHandler):
  def post(self):
    # Get'ticker' for the current process
    ticker = self.request.get("ticker") 
    
    # Get Analyst Estimates for the given ticker
    q = AnalystEstimate.query(AnalystEstimate.ticker == ticker,
                              AnalystEstimate.year >= Common.CURRENT_YEAR,
                              AnalystEstimate.year < (Common.CURRENT_YEAR + Common.SHOW_PERIODS)
                             ).order(AnalystEstimate.year)

    aEstList = []
    for p in q.iter(): 
      aEstList.append(p.ni)
      
    # Get records from 'YearlyFinanacial' table for the given ticker
    q = YearlyFinancial.query(YearlyFinancial.ticker == ticker,
                                YearlyFinancial.year >= (Common.CURRENT_YEAR-Common.SHOW_PERIODS)).order(YearlyFinancial.year)
      
    # Some stocks may not have data populated, do nothing in that case
    if (q.count() == 0):
      return
    
    data = numpy.zeros([Common.TOTAL_FIELDS, Common.SHOW_PERIODS])
    
    for p in q.iter():  
      yrCnt = p.year - (Common.CURRENT_YEAR-Common.SHOW_PERIODS)
       
      # If record is older than 5 years or newer than current year, skip
      if ( yrCnt >= Common.SHOW_PERIODS or yrCnt < 0 ):
       continue
      
      data[0, yrCnt] = p.sales
      data[1, yrCnt] = p.salesGrowth
      data[3, yrCnt] = p.niPerSales
      data[5, yrCnt] = p.depPerSales
      data[7, yrCnt] = p.defTaxesPerSales
      data[9, yrCnt] = p.otherPerSales
      data[11, yrCnt] = p.capExPerSales
      data[13, yrCnt] = p.wcDeltaPerSales
    
    # End of for loop for Yearly Financials
       
    # For sales, sales growth and ni, use last values. For everything else, use 5 year avg
    
    salesLast = data[0, 4]
    
    # If last value is not available, use average
    if (salesLast == None or salesLast == 0):
      salesLast = numpy.mean(filter(None, data[0]))

    # If we can't get a base value of sales, abort estimates  
    if (salesLast == None or salesLast == 0):
      return
       
    salesGrowthLast = data[1, 4]

    # If last value is not available, use average
    if (salesGrowthLast == None or salesGrowthLast == 0):
      salesGrowthLastF =  numpy.mean(filter(None, data[1]))
      
    # If we can't get a base value of salesGrowthLast, abort estimates  
    if (salesGrowthLast == None or salesGrowthLast == 0):
      return      
    
    niPerSalesLast = data[3, 4]
    
    # If last value is not available, Use average
    if (niPerSalesLast == None or niPerSalesLast == 0):
      niPerSalesLast = numpy.mean(filter(None, data[3]))

    # If we can't get a base value of niPerSalesLast, we may still have analyst estimates.  
      
    depPerSalesAvg = Common.getPastAvg(data[5])
    defTaxesPerSalesAvg = Common.getPastAvg(data[7])
    otherPerSalesAvg = Common.getPastAvg(data[9])
    capExPerSalesAvg = Common.getPastAvg(data[11])
    wcDeltaPerSalesAvg = Common.getPastAvg(data[13])

    
    curSales = 0
    
    # Calculate and update values for next 5 years
    for i in range(0, 5):
      year = Common.CURRENT_YEAR + i
      
      # Check if record already exists
      usf = UserStockForecast.query(UserStockForecast.user == Common.AVG_USER,
                                    UserStockForecast.ticker == ticker,        
                                    UserStockForecast.year == year).get()
      
      # If record does not exist, create it
      if (usf == None):
        usf = UserStockForecast(user = Common.AVG_USER,
                                ticker = ticker,        
                                year = year)
        usf.put()

      curSales = round(salesLast * (1 + (salesGrowthLast/100))) 
      if (curSales == 0):
        return
        
      salesLast = curSales
      
      # Update Sales
      usf.sales = curSales
      usf.salesGrowth = salesGrowthLast
      
      # Update ni
      # Use analyst estimate first if available
      if (len(aEstList) > i):
        usf.ni = aEstList[i]
        niPerSalesLast =  round( ((aEstList[i] * 100) / curSales), 2)  
        usf.niPerSales = niPerSalesLast             
      else:
        usf.ni = round(curSales * (niPerSalesLast/100))
        usf.niPerSales = niPerSalesLast
      
      usf.fcf = usf.ni
      
      if (depPerSalesAvg != None):
        usf.dep = round(curSales * (depPerSalesAvg/100))
        usf.depPerSales = depPerSalesAvg
        usf.fcf = usf.fcf + usf.dep

      if (defTaxesPerSalesAvg != None):
        usf.defTaxes = round(curSales * (defTaxesPerSalesAvg/100))
        usf.defTaxesPerSales = defTaxesPerSalesAvg
        usf.fcf = usf.fcf + usf.defTaxes

      if (otherPerSalesAvg != None):
        usf.other = round(curSales * (otherPerSalesAvg/100))
        usf.otherPerSales = otherPerSalesAvg
        usf.fcf = usf.fcf + usf.other
        
      if (capExPerSalesAvg != None):        
        usf.capEx = round(curSales * (capExPerSalesAvg/100))
        usf.capExPerSales = capExPerSalesAvg
        usf.fcf = usf.fcf - usf.capEx
      
      if (wcDeltaPerSalesAvg != None):        
        usf.wcDelta = round(curSales * (wcDeltaPerSalesAvg/100))
        usf.wcDeltaPerSales = wcDeltaPerSalesAvg
        usf.fcf = usf.fcf - usf.wcDelta
        
      
      usf.fcf = round(usf.fcf, 2)
      
      usf.put()
        
      
     
class ProcessCrowdEstimates(webapp2.RequestHandler):
  def get(self):
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return

    # Less Than and Greater Than or Equal To characters
    # Used to split big jobs. A to ZZZZZZZZZZZZ
    # lt='M', gte='M'
    lt = self.request.get("lt")
    if (lt == None or lt == ''):
      lt = 'ZZZZZZZZZZZZ'
      
    gte = self.request.get("gte")
    if (gte == None or gte == ''):
      gte = 'A'    

    # Get List of Tickers from table - Stock    
    stocks = Stock.query(Stock.exchange == exchange,
                         Stock.ticker < lt,
                         Stock.ticker >= gte)
                             
    # For each stock ticker,   
    for stock in stocks.iter():   
      taskqueue.add(url='/admin/ProcessCrowdEstimatesForStock', 
                    params={'ticker': stock.ticker, 'coe': stock.coe, 'shares_os': stock.shares_os, 'price': stock.price} )
                
    self.response.out.write("ProcessCrowdEstimates complete.")
    
    
class ProcessCrowdEstimatesForStock(webapp2.RequestHandler):
  def post(self):
    # Get'ticker' for the current process
    ticker = self.request.get("ticker") 
    coe = Common.parseFloat(self.request.get("coe"))
    shares_os = Common.parseFloat(self.request.get("shares_os"))
    price = Common.parseFloat(self.request.get("price"))
    
    # Used in Intrinsic Value calculation
    fcf = 0
    fcfList = []
    
    # For each year
    for yr in range(Common.CURRENT_YEAR, (Common.CURRENT_YEAR + Common.SHOW_PERIODS)): 
      q = UserStockForecast.query(UserStockForecast.ticker == ticker,        
                                  UserStockForecast.year == yr)
    
      # if no UserStockForecast present
      if (q.count() == 0):
        continue
                  
      # User Forecast Array     
      ufA = None
      
      for p in q.iter():
        # Data is counted only if FCF was calculated for that year
        if (p.fcf == 0 or p.fcf == None):
          continue
        
        if (ufA == None):
          ufA = numpy.array( [ 
                               [p.sales], [p.salesGrowth], [p.ni], [p.niPerSales], [p.dep], [p.depPerSales], 
                               [p.defTaxes], [p.defTaxesPerSales], [p.other], [p.otherPerSales], 
                               [p.capEx], [p.capExPerSales], [p.wcDelta], [p.wcDeltaPerSales], [p.fcf]
                             ]
                           )
        else:
          ufA = numpy.append(ufA, [ 
                                   [p.sales], [p.salesGrowth], [p.ni], [p.niPerSales], [p.dep], [p.depPerSales], 
                                   [p.defTaxes], [p.defTaxesPerSales], [p.other], [p.otherPerSales], 
                                   [p.capEx], [p.capExPerSales], [p.wcDelta], [p.wcDeltaPerSales], [p.fcf]
                                  ], 
                             axis=1 
                            )
      
      # Calculate and Update mean values in 'CrowdStockForecast' 
      if (ufA != None):
        # Check if record alreday exists in 'CrowdStockForecast'
        csf = CrowdStockForecast.query(CrowdStockForecast.ticker == ticker,        
                                       CrowdStockForecast.year == yr
                                      ).get() 

        # If not, create it
        if (csf == None):
          csf =  CrowdStockForecast(ticker = ticker, 
                                    year=yr)
          csf.put()        
   
        csf.sales = round(numpy.mean(filter(None,ufA[0])))
        csf.salesVar = round(numpy.var(filter(None,ufA[0])), 2)
        csf.salesGrowth = round(numpy.mean(filter(None,ufA[1])), 2)
        csf.salesGrowthVar = round(numpy.var(filter(None,ufA[1])), 2)
        
        csf.ni = round(numpy.mean(filter(None,ufA[2])))
        csf.niVar = round(numpy.var(filter(None,ufA[2])), 2)
        csf.niPerSales = round(numpy.mean(filter(None,ufA[3])), 2)
        csf.niPerSalesVar = round(numpy.var(filter(None,ufA[3])), 2)
        
        csf.dep = round(numpy.mean(filter(None,ufA[4])))
        csf.depVar = round(numpy.var(filter(None,ufA[4])), 2)
        csf.depPerSales = round(numpy.mean(filter(None,ufA[5])), 2) 
        csf.depPerSalesVar = round(numpy.var(filter(None,ufA[5])), 2)   

        csf.defTaxes = round(numpy.mean(filter(None,ufA[6])))
        csf.defTaxesVar = round(numpy.var(filter(None,ufA[6])), 2)
        csf.defTaxesPerSales = round(numpy.mean(filter(None,ufA[7])), 2)
        csf.defTaxesPerSalesVar = round(numpy.var(filter(None,ufA[7])), 2)
        
        csf.other = round(numpy.mean(filter(None,ufA[8])))
        csf.otherVar = round(numpy.var(filter(None,ufA[8])), 2)
        csf.otherPerSales = round(numpy.mean(filter(None,ufA[9])), 2)
        csf.otherPerSalesVar = round(numpy.var(filter(None,ufA[9])), 2)
        
        csf.capEx = round(numpy.mean(filter(None,ufA[10])))
        csf.capExVar = round(numpy.var(filter(None,ufA[10])), 2)
        csf.capExPerSales = round(numpy.mean(filter(None,ufA[11])), 2)
        csf.capExPerSalesVar = round(numpy.var(filter(None,ufA[11])), 2)
        
        csf.wcDelta = round(numpy.mean(filter(None,ufA[12])))
        csf.wcDeltaVar = round(numpy.var(filter(None,ufA[12])), 2)
        csf.wcDeltaPerSales = round(numpy.mean(filter(None,ufA[13])), 2)  
        csf.wcDeltaPerSalesVar = round(numpy.var(filter(None,ufA[13])), 2)

        fcf = round(numpy.mean(filter(None,ufA[14])))
        csf.fcf = fcf
        # Add FCF to list for later calculation of Intrinsic value
        fcfList.append(csf.fcf)
        
        csf.fcfVar = round(numpy.var(filter(None,ufA[12])), 2)

        csf.put()
        
      # End of if
        
    # End of for
 
    # Check if FCF is available for all the periods
    if (len(fcfList) == Common.SHOW_PERIODS):
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
      if (shares_os != 0):
        iValue = round(dfcfeTotal/shares_os, 2)
        # update Intrinsic Value in 'Stock'
        stock = Stock.query(Stock.ticker==ticker).get()
        
        if (stock != None):
          stock.terminalFcfe = terminalFcfe
          stock.fcfSum = dfcfeTotal
          stock.iValue = iValue

          if (iValue != None and price != None and iValue > 0):
            stock.pvRatio = round(price/iValue, 2) 
            stock.pvRatioDev = round(abs(1 - stock.pvRatio), 2)
            stock.put()


class calculatePVratioHandler(webapp2.RequestHandler):
  @ndb.toplevel
  def get(self):   
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return
      
    # Less Than and Greater Than or Equal To characters
    # Used to split big jobs. A to ZZZZZZZZZZZZ
    # lt='M', gte='M'
    lt = self.request.get("lt")
    if (lt == None or lt == ''):
      lt = 'ZZZZZZZZZZZZ'
      
    gte = self.request.get("gte")
    if (gte == None or gte == ''):
      gte = 'A'    

    # Get List of Tickers from table - Stock    
    stocks = Stock.query(Stock.exchange == exchange,
                         Stock.ticker < lt,
                         Stock.ticker >= gte)
    
    # For each stock ticker     
    for stock in stocks.iter():
      price = stock.price
      iValue = stock.iValue
      
      if (price != None and iValue != None and iValue > 0):
        stock.pvRatio = round(stock.price / stock.iValue, 2)
        stock.pvRatioDev = round(abs(1 - stock.pvRatio), 2)
        stock.put_async()
        
    self.response.out.write("calculatePVratio complete.")