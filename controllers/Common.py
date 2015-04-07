#!/usr/bin/env python

import os
import csv

from google.appengine.ext import ndb

import webapp2, logging, numpy, math

#from models import Models
from models.Models import Stock, UserStockForecast, YearlyFinancial, CrowdStockForecast

CURRENT_YEAR = 2014
AVG_USER = 'valuation.spreadsheet@gmail.com' 
SHOW_PERIODS = 5
TOTAL_FIELDS = 15
COMPANY_LIFE = 15

# Input: 12.20, (12.20), N/A
# Output: 12.20
def getEqFloat(numberStr):
  negativeFlag = False
  
  if (numberStr == '-' or numberStr == 'N/A' or numberStr == 'NA'):
   return None

  # Remove comma from number string
  numberStr = numberStr.replace(",", "")
  
  # Check if the first position is '(' : Signifies negative number
  if (numberStr[1:] == '('):
   # Ignore '()'
   numberStr = numberStr[1:-1]
   negativeFlag = True
  
  try:
    number = round(float(numberStr), 2)
  except:
    return None
    
  if (negativeFlag == True):
     number = 0 - number
     
  return number

  
# Input: 12.09M, 12.09B, (12.09M), N/A
# Output: 0.0 or valid million equivalent of given number
def getEqMillions(numberStr):
  negativeFlag = False
  
  if (numberStr == '-' or numberStr == 'N/A' or numberStr == 'NA'):
   return None
   
  # Remove comma from number string
  numberStr = numberStr.replace(",", "")
   
  # Check if the first position is '(' : Signifies negative number
  if (numberStr[0] == '('):
   # Ignore '()'
   numberStr = numberStr[1:-1]
   negativeFlag = True
  
  # Check if the last position is 'B' or 'M'
  lastPos = numberStr[-1:].upper()

  try:    
    if (lastPos == 'T'):
     number = float(numberStr[:-1]) * 1000.0 * 1000.0
     
    elif (lastPos == 'B'):
     number = float(numberStr[:-1]) * 1000.0
     
    elif (lastPos == 'M'):
     number = float(numberStr[:-1])
    
    else:
     number = float(numberStr) / 1000000.0
    
    number = round(number, 2)
  except:
    logging.info("Float value expected. Received: " + numberStr)
    logging.info("Replaced the value with NA")
    return None
  
  if (negativeFlag == True):
     number = 0 - number
     
  return number

def getRound(floatVal, intVal, default=None):
  if (floatVal==None or floatVal==''):
    return default
  else:
    return round(floatVal, intVal)

def parseFloat(string, default=None):
  try:
    return float(string)
  except ValueError:
    return default   

def parseInt(string, default=None):
  try:
    return int(string)
  except ValueError:
    return default    
    
# Get Past data for a given stock from YearlyFinancial
def getPastData(ticker):
  # Create multi-dimensional array for past data
  fcfDataPast = numpy.zeros([TOTAL_FIELDS,SHOW_PERIODS])
  
  if (ticker==None or ticker==""):
    return fcfDataPast
     
  # Get ticker financials data
  q = YearlyFinancial.query(YearlyFinancial.ticker == ticker,
                            YearlyFinancial.year < CURRENT_YEAR,
                            YearlyFinancial.year >= (CURRENT_YEAR-SHOW_PERIODS) 
                           ).order(YearlyFinancial.year)

  for p in q.iter():
    yrCnt = CURRENT_YEAR - p.year - 1
     
    # If record is older than 5 years or newer than current year, skip
    if ( yrCnt > (SHOW_PERIODS-1) or yrCnt < 0 ):
     continue

    fcfDataPast[0,yrCnt] = p.sales
    fcfDataPast[1,yrCnt] = p.salesGrowth
    fcfDataPast[2,yrCnt] = p.ni
    fcfDataPast[3,yrCnt] = p.niPerSales
    fcfDataPast[4,yrCnt] = p.dep
    fcfDataPast[5,yrCnt] = p.depPerSales
    fcfDataPast[6,yrCnt] = p.defTaxes
    fcfDataPast[7,yrCnt] = p.defTaxesPerSales
    fcfDataPast[8,yrCnt] = p.other
    fcfDataPast[9,yrCnt] = p.otherPerSales
    fcfDataPast[10,yrCnt] = p.capEx
    fcfDataPast[11,yrCnt] = p.capExPerSales
    fcfDataPast[12,yrCnt] = p.wcDelta
    fcfDataPast[13,yrCnt] = p.wcDeltaPerSales

    fcfDataPast[14,yrCnt] = p.fcf
  
  return fcfDataPast
  

# Get Forecast data for a given stock from UserStockForecast OR CrowdForecast
def getForecastData(ticker, userFlag, userName):
  # Create multi-dimensional array for past data
  fcfDataForecast = numpy.zeros([TOTAL_FIELDS,SHOW_PERIODS])
  
  if (ticker==None or ticker==""):
    return fcfDataForecast

  # if userFlag = 'N', get Crowd Forecast data               
  if (userFlag == 'N'):
    q = CrowdStockForecast.query(CrowdStockForecast.ticker == ticker,        
                                 CrowdStockForecast.year >= CURRENT_YEAR,
                                 CrowdStockForecast.year < (CURRENT_YEAR+SHOW_PERIODS),
                                ).order(CrowdStockForecast.year) 
          
  # else if userName is present, get User Forecast data
  elif (userName != ''):
    q = UserStockForecast.query(UserStockForecast.user == userName,
                                UserStockForecast.ticker == ticker,        
                                UserStockForecast.year >= CURRENT_YEAR,
                                UserStockForecast.year < (CURRENT_YEAR+SHOW_PERIODS),
                               ).order(UserStockForecast.year) 
  # else return empty result array
  else:
    return fcfDataForecast

  for p in q.iter():
    yrCnt =  p.year - CURRENT_YEAR
     
    # If record is more than 5 years in future, skip
    if ( yrCnt > (SHOW_PERIODS-1)):
     continue
         
    fcfDataForecast[0,yrCnt] = p.sales
    fcfDataForecast[1,yrCnt] = p.salesGrowth
    fcfDataForecast[2,yrCnt] = p.ni
    fcfDataForecast[3,yrCnt] = p.niPerSales
    fcfDataForecast[4,yrCnt] = p.dep
    fcfDataForecast[5,yrCnt] = p.depPerSales
    fcfDataForecast[6,yrCnt] = p.defTaxes
    fcfDataForecast[7,yrCnt] = p.defTaxesPerSales
    fcfDataForecast[8,yrCnt] = p.other
    fcfDataForecast[9,yrCnt] = p.otherPerSales
    fcfDataForecast[10,yrCnt] = p.capEx
    fcfDataForecast[11,yrCnt] = p.capExPerSales
    fcfDataForecast[12,yrCnt] = p.wcDelta
    fcfDataForecast[13,yrCnt] = p.wcDeltaPerSales
    
    fcfDataForecast[14,yrCnt] = p.fcf
        
  return fcfDataForecast  

def xformNan(input):
  if (str(input) == 'nan' or input == None):
    return ''
  else:
    return input


# get FCF record  
#{"id":"1", "rowName":"Sales", "n5_":sales[4], "n4_":sales[3], "n3_":sales[2], "n2_":sales[1], "n1_":sales[0], 
#"PastAvg":getPastAvg(sales), "n1":salesF[0], "n2":salesF[1], "n3":salesF[2], "n4":salesF[3], "n5":salesF[4] } 	
def getFcfRecord(id, rowName, rowId, fcfDataPast, fcfDataForecast, userFlag):
  record = {}
  record['id'] = id
  record['rowName'] = rowName
  
  # Add Past Data
  for i in range(1, SHOW_PERIODS+1):
    # First 'Sales Growth' figure
    if (rowId == 1 and i == 1):
      record['n' + str(SHOW_PERIODS-i+1) + '_'] = ''
    else:  
      record['n' + str(SHOW_PERIODS-i+1) + '_'] = xformNan(fcfDataPast[rowId, (SHOW_PERIODS-i)])
    
  # Add Past Average
  record['PastAvg'] = xformNan(getPastAvg(fcfDataPast[rowId]))

  # Add Forecast Data
  for i in range(1, SHOW_PERIODS+1):
    if (math.isnan(fcfDataForecast[rowId, (i-1)])):
      record['n' + str(i) ] = ''
    else:
      record['n' + str(i) ] = xformNan(fcfDataForecast[rowId, (i-1)])
    
  # Add Forecast Methods
  if (userFlag == 'N'):
    record['FM'] = ""
  else:
    if (rowId==1 or rowId==3 or rowId==5 or rowId==7 or rowId==9 or rowId==11 or rowId==13): 
      record['FM'] = getFMhtml_button(rowId)
    else:
      record['FM'] = ""
    
  return record
  
        
# Find average of list values (of type string)
def getPastAvg(list):
  avg = None
  listLen = len(list)
  sum = 0
  n = 0
  
  for i in range(0, listLen):
    if (list[i] != None):
      if (math.isnan(list[i]) == True):
        continue
      else:
        sum = sum + list[i]
        n = n + 1
   
  # At least one value is found
  if (n>0):
    avg = round((sum/n),2)
    
  return avg

# Return Forecast Methods html for FCF data
def getFMhtml(rowId):
  html = ""
  id = 'fm_' + str(rowId)
  
  html = '<select class="ForecastMethods>' + \
         '  <option value="A">Last year value</option>' + \
         '  <option value="B">Avg of last 5 years</option>' 
      
  if (rowId == 3):
         html = html + '  <option value="C">Analyst Estimates</option>' 
        
  html = html + '</select>'
  
  return html
         
         
# Return Forecast Methods html for FCF data
def getFMhtml_bs_dropdown(rowId):
  html = ""
  id = 'fm_' + str(rowId)
  
  
  html = '   <div class="dropdown">' + \
         '     <a id="' + id + '" href="#" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' + \
         '       Forecast Method' + \
         '       <span class="caret"></span>' + \
         '     </a>' + \
         '     <ul class="dropdown-menu" role="menu" aria-labelledby="' + id + '">' + \
         '       <li role="presentation"><a role="menuitem" tabindex="-1" href="#">Last year value</a></li>' + \
         '       <li role="presentation"><a role="menuitem" tabindex="-1" href="#">Avg of last 5 years</a></li>'
 
  if (rowId == 3):
    html = html + '<li role="presentation"><a role="menuitem" tabindex="-1" href="#">Analyst Estimates</a></li>'
    
  html = html + '</ul></div>'

  return html
  
# Return Forecast Methods html for FCF data
def getFMhtml_button(rowId):
  html = ""
  name = 'fm_' + str(rowId)
  idA = valueA = 'fm_A_' + str(rowId)
  idB = valueB = 'fm_B_' + str(rowId)
  idC = valueC = 'fm_C_' + str(rowId)
  
  html = html + \
         '<label class="radio-inline"> ' + \
         '<input type="radio" name="' + name + '" class="ForecastMethods" id="' + idA + '" value="' + valueA + '" ' + \
         'data-toggle="tooltip" data-placement="top" title="use last year numbers">A</label>' +  \
         '<label class="radio-inline"> ' + \
         '<input type="radio" name="' + name + '" class="ForecastMethods" id="' + idB + '" value="' + valueB + '" ' + \
         'data-toggle="tooltip" data-placement="top" title="use last 5 years average">B</label>' 
         
  if (rowId == 3):
    html = html + \
         '<label class="radio-inline"> ' + \
         '<input type="radio" name="' + name + '" class="ForecastMethods" id="' + idC + '" value="' + valueC + '" ' + \
         'data-toggle="tooltip" data-placement="top" title="use Analysts Estimates">C</label>' 

  return html  
