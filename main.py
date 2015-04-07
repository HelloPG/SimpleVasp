# Comment - Git

import webapp2

from controllers import Home, Vasp, Reports
		
application = webapp2.WSGIApplication([

 ('/', Home.MainHandler),
 
 ('/StockTickersJson', Home.StockTickerJsonHandler),	
  
 ('/About', Home.AboutHandler),

 ('/Top100', Reports.Top100Handler),
 ('/Reports/topDataFetch', Reports.topDataFetch),

 ('/AnalystRatings', Reports.AnalystRatingsHandler),
 ('/Reports/arDataFetch', Reports.arDataFetch),

 ('/EarningSurprises', Reports.EarningSurprisesHandler),
 ('/Reports/esDataFetch', Reports.esDataFetch),


 ('/vasp/LoadFCF', Vasp.LoadFCFHandler),
 ('/vasp/LoadCOE', Vasp.LoadCOEHandler),
 ('/vasp/LoadResult', Vasp.LoadResultHandler),
 ('/vasp/LoadCompare', Vasp.LoadCompareHandler),
 ('/vasp/EvalResult', Vasp.EvalResultHandler),
 ('/vasp/LoadAnalystEstimate', Vasp.LoadAnalystEstimate),
 ('/vasp/SaveVasp', Vasp.SaveVasp),
 
], debug=True)