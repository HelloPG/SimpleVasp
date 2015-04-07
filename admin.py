import webapp2

from controllers import LoadDataTasks, ProcessDataTasks, Home
		
application = webapp2.WSGIApplication([
  ('/admin/LoadMarketData', LoadDataTasks.LoadMarketData),
  
  ('/admin/UpdateFundamentals', LoadDataTasks.UpdateFundamentals),
  ('/admin/UpdateStockFundamentals', LoadDataTasks.UpdateStockFundamentals),

  ('/admin/LoadFinancials', LoadDataTasks.LoadFinancials),
  ('/admin/LoadStockFinancials', LoadDataTasks.LoadStockFinancials),

  ('/admin/UpdateAnalystEstimates', LoadDataTasks.UpdateAnalystEstimates),
  ('/admin/UpdateAnalystEstimatesForStock', LoadDataTasks.UpdateAnalystEstimatesForStock),
  
  ('/admin/LoadRelated', LoadDataTasks.LoadRelated),
  ('/admin/LoadStockRelated', LoadDataTasks.LoadStockRelated),
  
  ('/admin/UpdateRatios', LoadDataTasks.UpdateRatios),
  ('/admin/UpdateStockRatios', LoadDataTasks.UpdateStockRatios),  
  ('/admin/UpdatePrice', LoadDataTasks.UpdatePrice),
  ('/admin/LoadRatings', LoadDataTasks.LoadRatings),
  ('/admin/LoadEarningSurprises', LoadDataTasks.LoadEarningSurprises),
    
  ('/admin/UserStats', Home.UserStats), 
  ('/admin/Temp', LoadDataTasks.Temp), 
  
  ('/admin/TheVaspAvgForecast', ProcessDataTasks.TheVaspAvgForecast),
  ('/admin/TheVaspAvgForecastForStock', ProcessDataTasks.TheVaspAvgForecastForStock), 
  
 	('/admin/ProcessCrowdEstimates', ProcessDataTasks.ProcessCrowdEstimates),
  ('/admin/ProcessCrowdEstimatesForStock', ProcessDataTasks.ProcessCrowdEstimatesForStock),
  
  ('/admin/calculatePVratio', ProcessDataTasks.calculatePVratioHandler),
   
], debug=True)