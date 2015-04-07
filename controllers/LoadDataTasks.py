#!/usr/bin/env python

import os
import csv

from google.appengine.ext import ndb
from google.appengine.api import taskqueue

import webapp2
import logging
import datetime

from models.Models import MarketData, Stock, YearlyFinancial, AnalystEstimate, AnalystRating, EarningSurprise

from controllers import Common

    
# Update: Beta and Number of shares for all the stocks
class UpdateFundamentals(webapp2.RequestHandler):

  def get(self):
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return

    # Get latest Market Data
    q = MarketData.query().order(MarketData.entry_date).get()
    rf = q.Treasury10yrReturn
    rm = q.SP500Return
     
    # ticker, Beta, Number of Shares
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", exchange + '_fundamentals_data.csv')) 

    inputReader = csv.reader(inputFile, delimiter=':')
     
    for row in inputReader:
      # Add the task to the default queue.
      taskqueue.add(url='/admin/UpdateStockFundamentals', 
                    params={'exchange': exchange, 
                            'ticker': row[0], 'name': row[1], 'beta':Common.getEqFloat(row[2]), 
                            'shares_os':Common.getEqMillions(row[3]), 'price':Common.getEqFloat(row[4]),
                            'eps':Common.getEqFloat(row[5]),
                            'rf':rf, 'rm':rm
                           }
                   )
    
    inputFile.close()
    self.response.out.write("Fundamental data for Exchange=" + exchange + " in task queue.")
    

# Update individual stock data
class UpdateStockFundamentals(webapp2.RequestHandler):
  
  def post(self):
    # Get 'exchange' and 'ticker' for the current process
    exchange = self.request.get("exchange")
    ticker = self.request.get("ticker")
    name = self.request.get("name")
    beta = Common.parseFloat(self.request.get("beta"))
    shares_os = Common.parseFloat(self.request.get("shares_os"))
    price = Common.parseFloat(self.request.get("price"))
    rf = Common.parseFloat(self.request.get("rf"))
    rm = Common.parseFloat(self.request.get("rm"))
    eps = Common.parseFloat(self.request.get("eps"))
    
    # Calculate cost of Equity    
    if (beta== None):
      coe = rf + ( 1 * (rm - rf) )
    else:  
      coe = rf + ( float(beta) * (rm - rf) )
     
    coe = round(coe, 2)
    
    # Find 'Stock' record for this 'ticker'
    q = Stock.query(Stock.ticker == ticker, Stock.exchange == exchange)
    stockRecord = q.get()
    
    # If stock does not exist, create a new record
    if (stockRecord == None):
      stockRecord = Stock(ticker = ticker,
                          name = name,
                          exchange = exchange,
                          beta = beta,
                          shares_os = shares_os,
                          coe = coe,
                          price = price,
                          eps = eps
                         )
      stockRecord.put()
      
    else:      
      # Update data
      stockRecord.beta = beta
      stockRecord.shares_os = shares_os
      stockRecord.price = price
      stockRecord.coe = coe   # COE = RF + Beta(RM - RF)
      stockRecord.eps = eps
      stockRecord.put()
      

class LoadFinancials(webapp2.RequestHandler):

  def get(self):
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return
      
    # Ticker, Year, Sales, NetIncome, Depreciation, CapEx, wcDelta, debtDelta  
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", exchange + '_financials_data.csv')) 

    inputReader = csv.reader(inputFile, delimiter=':')
     
    prevSales = None
    prevTicker = "-1"
    
    for row in inputReader:
      tickerVal = row[0].upper()
      
      #Ticker is changed
      if (tickerVal != prevTicker):
        prevTicker = tickerVal
        prevSales = None
       
      yearVal = int(row[1])
      salesVal = Common.getEqMillions(row[2])
      niVal = Common.getEqMillions(row[3])
      depVal = Common.getEqMillions(row[4])
      defTaxesVal = Common.getEqMillions(row[5])
      otherVal = Common.getEqMillions(row[6])
      
      # Marketwatch prints negative values for 'Increase in WC and CapEx' so it can add to NI for calculating FCF
      # TheVasp subtracts those values therefore negate marketwatch values
      capExVal = Common.getEqMillions(row[7])
      if (capExVal != None):
        capExVal = 0 - float(capExVal)
        
      wcDeltaVal = Common.getEqMillions(row[8])
      if (wcDeltaVal != None):
        wcDeltaVal = 0 - float(wcDeltaVal)
     
      
      # Add the task to the default queue.
      taskqueue.add(url='/admin/LoadStockFinancials', 
                    params={'tickerVal': tickerVal, 'yearVal': yearVal, 'salesVal': salesVal, 'prevSales': prevSales,
                            'niVal':niVal, 'depVal':depVal, 'defTaxesVal': defTaxesVal, 'otherVal': otherVal,
                            'capExVal':capExVal, 'wcDeltaVal':wcDeltaVal
                           })
      
      # Current Sales is 'prevSales' for next year      
      prevSales = salesVal
        
    
    inputFile.close()
    self.response.out.write("Financial data for Exchange=" + exchange + " loaded.")
    
      
class LoadStockFinancials(webapp2.RequestHandler):

  def post(self):
    tickerVal = self.request.get("tickerVal")
    
    # Check first if stock is defined in 'Stock'
    # if not, no point in loading financial data
    q = Stock.query(Stock.ticker == tickerVal).get()
    
    if (q == None):
      return
    
    yearVal = Common.parseInt(self.request.get("yearVal"))
    salesVal = Common.parseFloat(self.request.get("salesVal"))
    prevSalesVal = Common.parseFloat(self.request.get("prevSales")) 
    salesGrowthVal = None    
    niVal = Common.parseFloat(self.request.get("niVal"))
    niPerSalesVal = None
    depVal = Common.parseFloat(self.request.get("depVal"))
    depPerSalesVal = None
    defTaxesVal = Common.parseFloat(self.request.get("defTaxesVal"))
    defTaxesPerSalesVal = None
    otherVal = Common.parseFloat(self.request.get("otherVal"))
    otherPerSalesVal = None
    
    capExVal = Common.parseFloat(self.request.get("capExVal"))
    capExPerSalesVal = None
    wcDeltaVal = Common.parseFloat(self.request.get("wcDeltaVal"))
    wcDeltaPerSalesVal = None
      
    fcf = None
    
    if (salesVal != None and salesVal != 0):
      fcf = 0
      
      if (niVal != None):
        niPerSalesVal = round( ( (niVal * 100) / salesVal ), 2)  
        fcf = niVal
        
      if (depVal != None): 
        depPerSalesVal = round( ( (depVal * 100) / salesVal ), 2)
        fcf = fcf + depVal

      if (defTaxesVal != None): 
        defTaxesPerSalesVal = round( ( (defTaxesVal * 100) / salesVal ), 2)
        fcf = fcf + defTaxesVal

      if (otherVal != None): 
        otherPerSalesVal = round( ( (otherVal * 100) / salesVal ), 2)
        fcf = fcf + otherVal
        
      if (capExVal != None):   
        capExPerSalesVal = round( ( (float(capExVal) * 100) / salesVal ), 2)
        fcf = fcf - float(capExVal)
        
      if (wcDeltaVal != None):   
        wcDeltaPerSalesVal = round( ( (wcDeltaVal * 100) / salesVal ), 2)
        fcf = fcf - wcDeltaVal
        
      if (prevSalesVal != None and prevSalesVal != 0):
        salesGrowthVal = round( ( ( (salesVal - prevSalesVal)*100) / prevSalesVal), 2)
    
    # Check if the record already exists
    stockFin = YearlyFinancial.query(YearlyFinancial.ticker == tickerVal, YearlyFinancial.year == yearVal).get()
    
    # If record does not exist, create it
    if (stockFin == None):
      stockFin = YearlyFinancial(ticker = tickerVal, year = yearVal)
      stockFin.put()
      
    stockFin.sales = salesVal
    stockFin.ni = niVal
    stockFin.dep = depVal
    stockFin.defTaxes = defTaxesVal
    stockFin.other = otherVal
    stockFin.capEx = capExVal
    stockFin.wcDelta = wcDeltaVal
    
    if (fcf != None):
      stockFin.fcf = round(fcf)
    
    stockFin.salesGrowth = salesGrowthVal
    stockFin.niPerSales = niPerSalesVal
    stockFin.depPerSales = depPerSalesVal
    stockFin.defTaxesPerSales = defTaxesPerSalesVal
    stockFin.otherPerSales = otherPerSalesVal
    stockFin.capExPerSales = capExPerSalesVal
    stockFin.wcDeltaPerSales = wcDeltaPerSalesVal
             
    stockFin.put()

    
########################################

class LoadMarketData(webapp2.RequestHandler):
  def get(self):
    mktData = MarketData(Treasury10yrReturn=2.54, SP500Return=5.0)          
    mktData.put()
    self.response.out.write("Market data loaded.")

########################################

# temp
class Temp(webapp2.RequestHandler):
  @ndb.toplevel
  def get(self):
    q = UserStockForecast.query()

    for p in q.iter():
      #x = 2
      p.key.delete_async()
      
    self.response.out.write("Temp admin process complete.")
  

class UpdateStock(webapp2.RequestHandler):
  @ndb.toplevel
  def get(self):
    q = Stock.query(Stock.exchange != 'NYSE')

    for p in q.iter():
      p.exchange = 'NYSE'
      p.put_async()
      
    self.response.out.write("Temp admin process complete.")
    
    
class DeleteLocalData(webapp2.RequestHandler):
  def get(self):
    # Delete 'Stock' data
    q = Stock.query()

    for p in q.iter():
      p.key.delete()

    # Delete 'UserStock' data
    q = UserStock.query()

    for p in q.iter():
      p.key.delete()
      
    # Delete 'YearlyFinancial' data
    q = YearlyFinancial.query()

    for p in q.iter():
      p.key.delete()

    # Delete 'UserStockForecast' data
    q = UserStockForecast.query()

    for p in q.iter():
      p.key.delete()      

    # Delete 'CrowdStockForecast' data
    q = UserStockForecast.query()

    for p in q.iter():
      p.key.delete()   
      
      
    self.response.out.write("Temp admin process complete.") 


########################################    


# Update: estimates for all the stocks
class UpdateAnalystEstimates(webapp2.RequestHandler):

  def get(self):
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return

    # Estimate data
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", exchange + '_estimates_data.csv')) 

    inputReader = csv.reader(inputFile, delimiter=':')
     
    prevTicker = "-1"
     
    # ticker:year:estimate:shares_os: 
    for row in inputReader:
      ticker = row[0]
      
      if (ticker != prevTicker):
        year = Common.CURRENT_YEAR
        prevTicker = ticker
      else:
        year = year + 1

      niEst = Common.getEqFloat(row[2])
        
      # If niEst is not defined, nothing can be done about this data
      if (row[2] == None):
        return

      shares_os = Common.getEqMillions(row[3]) 
      
      # If shares_os is not defined, nothing can be done about this data
      if (shares_os == None):
        return

      # Add the task to the default queue.
      taskqueue.add(url='/admin/UpdateAnalystEstimatesForStock', 
                    params={'ticker': ticker, 'exchange': exchange, 'year': year, 'niEst':niEst, 'shares_os':shares_os})
    
    inputFile.close()
    self.response.out.write("Analyst Estimate data for Exchange=" + exchange + " in task queue.")
    

# Update Analyst Estimates for - individual stock
class UpdateAnalystEstimatesForStock(webapp2.RequestHandler):
  
  def post(self):
    ticker = self.request.get("ticker")
    exchange = self.request.get("exchange")
    year = Common.parseInt(self.request.get("year"))
    niEst = Common.parseFloat(self.request.get("niEst"))
    shares_os = Common.parseFloat(self.request.get("shares_os"))

    # Find 'AnalystEstimate' record for this 'ticker'
    ae = AnalystEstimate.query(AnalystEstimate.ticker == ticker, AnalystEstimate.exchange == exchange, AnalystEstimate.year == year).get()
    
    # If AnalystEstimate does not exist, create a new record
    if (ae == None):
      ae = AnalystEstimate(ticker = ticker,
                           exchange = exchange,
                           year = year,
                           ni = round((shares_os * niEst), 2)
                         )
      
    else:      
      # Update data
      ae.ni = round((shares_os * niEst), 2)

    ae.put()
    

        
########################################      

class LoadRelated(webapp2.RequestHandler):

  def get(self):
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return
      
    # Ticker, Year, Sales, NetIncome, Depreciation, CapEx, wcDelta, debtDelta  
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", exchange + '_related_data.csv')) 

    inputReader = csv.reader(inputFile, delimiter=':')

    for row in inputReader:
      tickerVal = row[0].upper()
      relatedVal = row[1]

      # Add the task to the default queue.
      taskqueue.add(url='/admin/LoadStockRelated', 
                    params={'tickerVal': tickerVal, 'relatedVal': relatedVal
                           })
         
    inputFile.close()
    self.response.out.write("Related data for Exchange=" + exchange + " loaded.")

# Load Related companies for - individual stock
class LoadStockRelated(webapp2.RequestHandler):
  
  def post(self):
    ticker = self.request.get("tickerVal")
    related = self.request.get("relatedVal")
    
    # Find 'Stock' record for this 'ticker'
    st = Stock.query(Stock.ticker == ticker).get()
    
    if (st != None):
      st.related = related
      st.put()
      
########################################      

class UpdateRatios(webapp2.RequestHandler):

  def get(self):
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return
      
    # Ticker, Year, Sales, NetIncome, Depreciation, CapEx, wcDelta, debtDelta  
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", exchange + '_ratios_data.csv')) 

    inputReader = csv.reader(inputFile, delimiter=':')

    for row in inputReader:
      ticker = row[0].upper()
      peRatio = row[1]
      pbRatio = row[2]

      # Add the task to the default queue.
      taskqueue.add(url='/admin/UpdateStockRatios', 
                    params={'ticker': ticker, 'peRatio': peRatio, 'pbRatio': pbRatio
                           })
         
    inputFile.close()
    self.response.out.write("Ratios for Exchange=" + exchange + " loaded.")

# Load Ratio Data for - individual stock
class UpdateStockRatios(webapp2.RequestHandler):
  
  def post(self):
    ticker = self.request.get("ticker")
    peRatio = Common.parseFloat(self.request.get("peRatio"))
    pbRatio = Common.parseFloat(self.request.get("pbRatio"))
    
    # Find 'Stock' record for this 'ticker'
    st = Stock.query(Stock.ticker == ticker).get()
    
    if (st != None):
      price = st.price

      if (price == None):
        return

      if (peRatio == None):
        eps = None
      else:
        eps = round(price / peRatio, 2)

      if (pbRatio == None):
        bps = None
      else:
        bps = round(price / pbRatio, 2)

      st.eps = eps
      st.bps = bps
      st.put()
      
########################################      

class UpdatePrice(webapp2.RequestHandler):
  def get(self):
    # Get 'exchange' for the current process
    exchange = self.request.get("Exchange")
    
    if (exchange == None or exchange == ''):
      self.response.out.write("Exchange not specified.")
      return
      
    # Ticker, Year, Sales, NetIncome, Depreciation, CapEx, wcDelta, debtDelta  
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", exchange + '_price_data.csv')) 

    inputReader = csv.reader(inputFile, delimiter=',')

    for row in inputReader:
      ticker = row[0].upper()
      price = Common.parseFloat(row[5])

      # Find 'Stock' record for this 'ticker'
      st = Stock.query(Stock.ticker == ticker).get()
      
      if (st != None):
        if (price != None):
          st.price = price

          if (st.iValue != None and price != 0):
            st.ivPrem = round ((st.iValue-price)/price, 2)

          if (st.eps != None and st.eps != 0):
            st.peRatio = round (price/st.eps, 2)

          if (st.bps != None and st.bps != 0):
            st.pbRatio = round (price/st.bps, 2)

          st.put()
         
    inputFile.close()
    self.response.out.write("New Prices for Exchange=" + exchange + " updated.")


########################################      

class LoadRatings(webapp2.RequestHandler):
  def get(self):
    # Ticker, Analyst, Old, New 
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", 'ratings_data.csv')) 

    inputReader = csv.reader(inputFile, delimiter=':')
    date = None

    for row in inputReader:
      ticker = row[0].upper()

      # Do it only once
      if (date == None):
        date = datetime.datetime.strptime(row[4], '%m/%d/%Y').date()

      # Check if the record already exists
      ar = AnalystRating.query(AnalystRating.ticker==row[0],
                               AnalystRating.analyst==row[1],
                               AnalystRating.date==date,
                              ).get()

      # if yes, this is a repeat file, abort
      if (ar != None):
        self.response.out.write("Ratings file was already loaded.")
        return

      # Insert into AnalystRating
      ar = AnalystRating(ticker = row[0].upper(),
                         analyst= row[1],
                         oldRating = row[2],
                         newRating = row[3],
                         date = date,
                         direction = row[5]
                        )
          
      ar.put()
         
    inputFile.close()
    self.response.out.write("Analyst ratings loaded.")


########################################

class LoadEarningSurprises(webapp2.RequestHandler):
  def get(self):
    inputFile = open(os.path.join(os.path.dirname(__file__) + "/data", 'earningSurprises_data.csv'))

    inputReader = csv.reader(inputFile, delimiter=':')
    date = None

    for row in inputReader:
      ticker = row[0].upper()

      # Do it only once
      if (date == None):
        date = datetime.datetime.strptime(row[4], '%m/%d/%Y').date()

      # Check if the record already exists
      es = EarningSurprise.query(EarningSurprise.ticker==row[0],
                                 EarningSurprise.date==date,
                                ).get()

      # if yes, this is a repeat file, abort
      if (es != None):
        self.response.out.write("Earning Surprise file was already loaded.")
        return

      # Insert into EarningSurprise
      es = EarningSurprise(ticker = row[0].upper(),
                           actual= Common.parseFloat(row[1]),
                           estimate = Common.parseFloat(row[2]),
                           percentSurprise = Common.parseFloat(row[3]),
                           date = date,
                           direction = row[5]
                          )

      es.put()

    inputFile.close()
    self.response.out.write("Earning Surprises loaded.")