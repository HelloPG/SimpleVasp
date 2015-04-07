#!/usr/bin/env python

import datetime
from google.appengine.ext import ndb
from google.appengine.api import users


class MarketData(ndb.Model):
  Treasury10yrReturn = ndb.FloatProperty()
  SP500Return = ndb.FloatProperty()
  entry_date = ndb.DateProperty(auto_now=True)
  
class Stock(ndb.Model):
  ticker = ndb.StringProperty(required=True)
  exchange = ndb.StringProperty(required=True)
  name = ndb.StringProperty()
  related = ndb.StringProperty()

  shares_os = ndb.FloatProperty()
  eps = ndb.FloatProperty()
  bps = ndb.FloatProperty()  # Book Value per Share
  beta = ndb.FloatProperty()
  coe = ndb.FloatProperty() # Cost of Equity - Current value. Updated when Beta/RF/RM are changed.
  earnings = ndb.FloatProperty()

  price = ndb.FloatProperty()  # Current Price - Updated weekly/daily?

  terminalFcfe = ndb.FloatProperty()
  fcfSum = ndb.FloatProperty()

  iValue = ndb.FloatProperty()  # Crowd Intrinsic Value. Calculated during - ProcessCrowdEstimates

  # Calculated  During daily price update
  ivPrem = ndb.FloatProperty() # (iValue - price) / price
  peRatio = ndb.FloatProperty() # price / earnings
  pbRatio = ndb.FloatProperty() # price / Book Value

  entry_date = ndb.DateProperty(auto_now=True)
  
class AnalystEstimate(ndb.Model):
  ticker = ndb.StringProperty(required=True)
  exchange = ndb.StringProperty(required=True)
  year = ndb.IntegerProperty(required=True)
  ni = ndb.FloatProperty()

class AnalystRating(ndb.Model):
  ticker = ndb.StringProperty(required=True)
  analyst = ndb.StringProperty(required=True)
  date = ndb.DateProperty(required=True)
  oldRating = ndb.StringProperty()  # sell, underperform, hold/marketperform/neutral, buy, strongbuy
  newRating = ndb.StringProperty()
  direction = ndb.StringProperty()

class EarningSurprise(ndb.Model):
  ticker = ndb.StringProperty(required=True)
  date = ndb.DateProperty(required=True)
  period = ndb.StringProperty()
  actual = ndb.FloatProperty()
  estimate = ndb.FloatProperty()
  percentSurprise = ndb.FloatProperty()
  direction = ndb.StringProperty()

class YearlyFinancial(ndb.Model):
  ticker = ndb.StringProperty(required=True)
  year = ndb.IntegerProperty(required=True)
  sales = ndb.FloatProperty()
  ni = ndb.FloatProperty()
  dep = ndb.FloatProperty()
  defTaxes = ndb.FloatProperty()
  other = ndb.FloatProperty()
  
  capEx = ndb.FloatProperty()  
  wcDelta = ndb.FloatProperty()    # Increase in WC

  salesGrowth = ndb.FloatProperty()	
  niPerSales = ndb.FloatProperty()	
  depPerSales = ndb.FloatProperty()	
  defTaxesPerSales = ndb.FloatProperty()	
  otherPerSales = ndb.FloatProperty()	
  
  capExPerSales = ndb.FloatProperty()
  wcDeltaPerSales = ndb.FloatProperty()    

  fcf = ndb.FloatProperty()  # fcf = ni + dep - capEx - wcDelta + debtDelta
  entry_date = ndb.DateProperty(auto_now=True)
  
class CrowdStockForecast(ndb.Model):
  ticker = ndb.StringProperty(required=True)
  year = ndb.IntegerProperty(required=True)
  group = ndb.StringProperty()
  
  sales = ndb.FloatProperty()
  ni = ndb.FloatProperty()
  dep = ndb.FloatProperty()
  defTaxes = ndb.FloatProperty()
  other = ndb.FloatProperty()
  
  capEx = ndb.FloatProperty()  
  wcDelta = ndb.FloatProperty()      # Increase in WC
  
  salesGrowth = ndb.FloatProperty() 
  niPerSales = ndb.FloatProperty()	
  depPerSales = ndb.FloatProperty()	
  defTaxesPerSales = ndb.FloatProperty()
  otherPerSales = ndb.FloatProperty()
  
  capExPerSales = ndb.FloatProperty()	
  wcDeltaPerSales = ndb.FloatProperty()
 
  fcf = ndb.FloatProperty()          # fcf = ni + dep - capEx - wcDelta + debtDelta
  
  salesVar = ndb.FloatProperty()
  niVar = ndb.FloatProperty()
  depVar = ndb.FloatProperty()
  defTaxesVar = ndb.FloatProperty()
  otherVar = ndb.FloatProperty()
  
  capExVar = ndb.FloatProperty()  
  wcDeltaVar = ndb.FloatProperty()      
   
  salesGrowthVar = ndb.FloatProperty() 
  niPerSalesVar = ndb.FloatProperty()	
  depPerSalesVar = ndb.FloatProperty()	
  defTaxesPerSalesVar = ndb.FloatProperty()
  otherPerSalesVar = ndb.FloatProperty()
  
  capExPerSalesVar = ndb.FloatProperty()	
  wcDeltaPerSalesVar = ndb.FloatProperty()
 
  fcfVar = ndb.FloatProperty()          
  
  entry_date = ndb.DateProperty(auto_now=True)  
  
class VaspUser(ndb.Model):
  user = ndb.StringProperty(required=True)
  entry_date = ndb.DateProperty(auto_now=True)
  
class VaspGroup(ndb.Model):
  name = ndb.StringProperty(required=True)
  description = ndb.StringProperty()
  entry_date = ndb.DateProperty(auto_now=True)
  
class UserGroup(ndb.Model):
  group = ndb.StringProperty(required=True)
  user = ndb.StringProperty(required=True)
  entry_date = ndb.DateProperty(auto_now=True)
   
class UserStock(ndb.Model):
  user = ndb.StringProperty(required=True)
  pseudoname = ndb.StringProperty()    # Used for publishing user's stock valuation
  ticker = ndb.StringProperty(required=True)
  companyName = ndb.StringProperty()
  terminalFcfe = ndb.FloatProperty()
  fcfSum = ndb.FloatProperty()
  iValue = ndb.FloatProperty()
  entry_date = ndb.DateProperty(auto_now=True)
   
class UserStockForecast(ndb.Model):
  user = ndb.StringProperty(required=True)
  ticker = ndb.StringProperty(required=True)
  year = ndb.IntegerProperty(required=True)

  sales = ndb.FloatProperty()
  ni = ndb.FloatProperty()
  dep = ndb.FloatProperty()
  defTaxes = ndb.FloatProperty()
  other = ndb.FloatProperty()
  
  capEx = ndb.FloatProperty()   
  wcDelta = ndb.FloatProperty()      # Increase in WC
  
  salesGrowth = ndb.FloatProperty()	
  niPerSales = ndb.FloatProperty()	
  depPerSales = ndb.FloatProperty()	
  defTaxesPerSales = ndb.FloatProperty()
  otherPerSales = ndb.FloatProperty()
  
  capExPerSales = ndb.FloatProperty()	
  wcDeltaPerSales = ndb.FloatProperty()

  fcf = ndb.FloatProperty()  
  entry_date = ndb.DateProperty(auto_now=True)  


