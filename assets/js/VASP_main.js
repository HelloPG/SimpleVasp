
		
$(document).ready(function () {
	$("#crowdVasp").prop("checked",true);
	$("#FM_Label").hide();
	renderFCF();
	renderResult();
	renderCOE();
	renderCompare();
	
	// If 'pubTicker' is set, this is a published valuation url. Trigger data fetch
	if (pubTicker != '')
		publishValuation(pubTicker, pubToken, pubCompanyName);
});


// Called from 'My Stocks'
function setCurrentTicker(ticker, token, companyName)
{
	$("#myVasp").prop("checked",true);
	$("#SaveLink").show();
	$("#FM_Label").show();

	$("#ticker").val(ticker);
	$('#companyName').text(companyName);

	loadCOEData(ticker);
	loadFCFData(ticker, '');
}

function publishValuation(ticker, token, companyName)
{
	$("#ticker").val(ticker);
	$("#companyName").text(companyName);
	loadCOEData(ticker);
	loadFCFData(ticker, token);
} 

// Called when user types stock symbol in typeahead.
$('.typeahead').on('typeahead:selected', function(evt, item) {
	$("#companyName").text(item.name);
	loadCOEData(item.ticker);
	loadFCFData(item.ticker, '');
})


function crowdVaspSelected()
{
	// hide 'SaveLink'
	$("#SaveLink").hide();
	$("#FM_Label").hide();
	
	// Change table rendering
	setCrowdVaspFlag(true);
	//$('#FreeCashFlow').handsontable('render');
	
	// If Ticker is set, refresh FCF data 
	var ticker = $("#ticker").val();

	if (ticker !=null && ticker != "")
		loadFCFData(ticker, '');			
	
	
}

function myVaspSelected()
{
	// Show 'SaveLink'
	$("#SaveLink").show();
	//$('#PublicUrl').show();
	$("#FM_Label").show();
	
	// Change table rendering
	setCrowdVaspFlag(false);
	//$('#FreeCashFlow').handsontable('render');

	// If Ticker is set, refresh FCF data 
	var ticker = $("#ticker").val();

	if (ticker !=null && ticker != "")
		loadFCFData(ticker, '');			
}


function loadCOEData(ticker)
{
  var htCOE = $('#CostOfEquity').data('handsontable');
  var htResult = $('#Result').data('handsontable');

  $.ajax({
	url: "/vasp/LoadCOE",
	dataType: 'json',
	data: JSON.stringify({ 'ticker': ticker}),			
	type: 'POST',
	success: function (res) 
		{
			htCOE.loadData(res.coeData);
			htResult.loadData(res.resultData);
		},
	error: function(xhr, status, error) 
		{
			$('#vasp_modal .modal-body').html(error);
			$("#vasp_modal").modal('show');	
		}

	});
}


function loadFCFData(ticker, token)
{
  var htFCF = $('#FreeCashFlow').data('handsontable');
  var htResult = $('#Result').data('handsontable');
  
  var userFlag = 'N';
  
  if($('#myVasp').is(':checked')){
	userFlag = 'Y';
  }

  $.ajax({
	url: "/vasp/LoadFCF",
	dataType: 'json',
	data: JSON.stringify({ 'ticker': ticker, 'token': token, 'userFlag': userFlag}),
	type: 'POST',
	success: function (res) 
		{
			if (res.errMessage != null)
			{
				$('#vasp_modal .modal-body').html(res.errMessage);
				$("#vasp_modal").modal('show');
			}
			else
			{
				// Clear current result values
				htResult.setDataAtCell(0, 3, '');
				htResult.setDataAtCell(1, 3, '');
				htResult.setDataAtCell(4, 3, '');
				
				if($('#myVasp').is(':checked'))
					setCrowdVaspFlag(false);
				
				// Set data values
				htFCF.loadData(res.fcfData);
				
				// Set publicUrlHtml
				$('#PublicUrl').html(res.publicUrlHtml);
				
				// If last sales = 0, don't allow user entry
				if ((res.fcfData[0]['n1_']) == 0)
				{
					$("#myVasp").attr("disabled", true);
					$("#SaveLink").hide();
					$('#vasp_modal .modal-body').html("Outside the scope of TheVasp. Either the stock is from finance industry  or Data is not available.");
					$("#vasp_modal").modal('show');	
					return;
				}
							
				loadResultData(ticker, userFlag, token);
				
				loadCompareData(ticker, userFlag, token);
			}
			
			// Use FCF values to draw visualization chart
			drawVisualizationChart(res.fcfData);
		},
	error: function(xhr, status, error) 
		{
			//$('#vasp_modal .modal-body').html(xhr.responseText);
			$('#vasp_modal .modal-body').html(error);
			$("#vasp_modal").modal('show');		
		}

	});
}

function loadResultData(ticker, userFlag, token)
{
  var htResult = $('#Result').data('handsontable');
  
  $.ajax({
	url: "/vasp/LoadResult",
	dataType: 'json',
	data: JSON.stringify({ 'ticker': ticker, 'userFlag': userFlag, 'token': token}),			
	type: 'POST',
	success: function (res) 
		{
			htResult.loadData(res.resultData);
		},
	error: function(xhr, status, error) 
		{
			$('#vasp_modal .modal-body').html(error);
			$("#vasp_modal").modal('show');	
		}

	});
}

function loadCompareData(ticker, userFlag, token)
{
  var htCompare = $('#Compare').data('handsontable');
  
  $.ajax({
	url: "/vasp/LoadCompare",
	dataType: 'json',
	data: JSON.stringify({ 'ticker': ticker, 'userFlag': userFlag, 'token': token}),			
	type: 'POST',
	success: function (res) 
		{
			htCompare.loadData(res.compareData);

			// draw compare chart
			drawCompareChart(res.compareData);
		},
	error: function(xhr, status, error) 
		{
			$('#vasp_modal .modal-body').html(error);
			$("#vasp_modal").modal('show');	
		}

	});
}

function evalResultData(fcfList)
{
  var htResult = $('#Result').data('handsontable');
  var htCoe = $('#CostOfEquity').data('handsontable');

  var coe = htCoe.getDataAtCell(4, 2);
  var nbrOfShares = htResult.getDataAtCell(2, 3);
  var price = htResult.getDataAtCell(5, 3);
	
  $.ajax({
	url: "/vasp/EvalResult",
	dataType: 'json',
	data: JSON.stringify({ 'fcfList': fcfList, 'coe': coe, 'nbrOfShares': nbrOfShares, 'price': price}),
	type: 'POST',
	success: function (res) 
		{
			htResult.loadData(res.resultData);
		},
	error: function(xhr, status, error) 
		{
			$('#vasp_modal .modal-body').html(error);
			$("#vasp_modal").modal('show');	
		}

	});
}

function saveVasp()
{
  var htFCF = $('#FreeCashFlow').data('handsontable');

  var ticker = $('#ticker').val(); 	

  // If ticker is not specified, no save
  if (ticker==null || ticker==""){
	$('#vasp_modal .modal-body').html("<p>Stock symbol not specified. Save ignored&hellip;</p>");
	$("#vasp_modal").modal('show');
	return;
  }

  // Get CompanyName 
  var companyName = $('#companyName').text();
  
  $.ajax({
	url: "/vasp/SaveVasp",
	dataType: "json",
	data: JSON.stringify({ 'dataFCF': htFCF.getData(), 'ticker': ticker, 'companyName': companyName }),
	type: 'POST',
	success: function (res) 
		{
			if (res.result === 'ok') {
				$('#vasp_modal .modal-body').html("<p>Spreadsheet was saved successfully&hellip;</p>");
				$("#vasp_modal").modal('show');
			}
			else {
				$('#vasp_modal .modal-body').html("<p>Spreadsheet save failed&hellip;</p>");
				$("#vasp_modal").modal('show');
			}
		},
	error: function () 
		{
			$('#vasp_modal .modal-body').html("<p>Spreadsheet save failed&hellip;</p>");
			$("#vasp_modal").modal('show');
		}

	});
}


// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
var visualization_chart;
var compare_chart;

function initChart() {
	// Instantiate visualization chart
	visualization_chart = new google.visualization.ColumnChart(document.getElementById('visualization_chart_div'));

	// Instantiate compare chart
	compare_chart = new google.visualization.ScatterChart(document.getElementById('compare_chart_div'));
}

function drawVisualizationChart(dataFCF) {
    var ticker = $('#ticker').val(); 
  
	// If ticker is not specified, return
	if (ticker==null || ticker=="")
		return;
	
	// Create the data table.
	var data = new google.visualization.DataTable();
	data.addColumn('number', 'Year');
	data.addColumn('number', 'Net Income');
	data.addColumn('number', 'Depreciation');
	data.addColumn('number', 'Deferred Taxes');
	data.addColumn('number', 'Other Funds');
	data.addColumn('number', 'CapEx');
	data.addColumn('number', 'Chg in WC');
	
	var year = 0;
	var value = 0;
	var index = '';
	
	for (i=5; i>0; i--)
	{
		year = 2014 - i;
		index = 'n' + i + '_';
		data.addRow([year, parseFloat(dataFCF[2][index]), 
						   parseFloat(dataFCF[4][index]), 
						   parseFloat(dataFCF[6][index]), 
						   parseFloat(dataFCF[8][index]), 
						   parseFloat(dataFCF[10][index]),
						   parseFloat(dataFCF[12][index])
					]);
	}
	
	for (i=0; i<5; i++)
	{
		year = 2014 + i;
		index = 'n' + (i + 1);
		data.addRow([year, parseFloat(dataFCF[2][index]), 
						   parseFloat(dataFCF[4][index]), 
						   parseFloat(dataFCF[6][index]), 
						   parseFloat(dataFCF[8][index]), 
						   parseFloat(dataFCF[10][index]),
						   parseFloat(dataFCF[12][index])
					]);
	}
		
	// Set chart options
	var options = {'title':'FCFE = Net Income + Depreciation + Deferred Taxes + Other Funds - CapEx - Increase in WC',
					hAxis: {title: 'Year', titleTextStyle: {color: 'red'}}, 
					vAxis: {title: "Dollar Amount in Millions", titleTextStyle: {color: 'red'}},
				   'width':1100,
				   'height':350};


	visualization_chart.draw(data, options);
}

function drawCompareChart3(dataCompare) {
    var ticker = $('#ticker').val();

	// If ticker is not specified, return
	if (ticker==null || ticker=="")
		return;

	// Create the data table.
	var data = new google.visualization.DataTable();
	data.addColumn('string', 'Ticker');
	data.addColumn('number', '(P/iV)');


	for (i=0; i<dataCompare.length; i++)
	{
		data.addRow([dataCompare[i]['ticker'],
					 parseFloat(dataCompare[i]['pvRatio'])
					]);
	}

	// Set chart options
	var options = {'title':'',
					//hAxis: {title: 'Ticker', titleTextStyle: {color: 'red'}},
					//vAxis: {title: "Dollar Amount in Millions", titleTextStyle: {color: 'red'}},
				   'width':1000,
				   'height':150};


	compare_chart.draw(data, options);
}

function drawCompareChart(dataCompare) {
    var ticker = $('#ticker').val();

	// If ticker is not specified, return
	if (ticker==null || ticker=="")
		return;

	// Create the data table.
	var data = new google.visualization.DataTable();
	data.addColumn('string', 'Ticker');
	data.addColumn('number', '(P/iV)*5');
	data.addColumn('number', 'P/BV');
	data.addColumn('number', '(P/E)/15');

	for (i=0; i<dataCompare.length; i++)
	{
		data.addRow([dataCompare[i]['ticker'],
					 Math.round(parseFloat(dataCompare[i]['pvRatio'])*5, 2),
					 parseFloat(dataCompare[i]['pbRatio']),
					 Math.round(parseFloat(dataCompare[i]['peRatio'])/15, 2)
					]);
	}

	// Set chart options
	var options = {'title':'Values are transformed for ease of comparison',
					//hAxis: {title: 'Ticker', titleTextStyle: {color: 'red'}},
					//vAxis: {title: "Dollar Amount in Millions", titleTextStyle: {color: 'red'}},
				   'width':1000,
				   'height':350};


	compare_chart.draw(data, options);
}

function drawCompareChart2(dataCompare) {
    var ticker = $('#ticker').val();

	// If ticker is not specified, return
	if (ticker==null || ticker=="")
		return;

	// Create the data table.
	var data = new google.visualization.DataTable();

	var total = dataCompare.length;
	var dataRows =  new Array(3);
	for (i=0; i<3; i++)
		dataRows[i] = new Array(total+1);

	data.addColumn('string', 'Category');

	dataRows[0][0] = "(Price/iValue)*5";
	dataRows[1][0] = "Price/BookValue";
	dataRows[2][0] = "(Price/Earnings)/15";

	// For each ticker
	for (i=0; i<total; i++)
	{
		data.addColumn('number', dataCompare[i]['ticker']);

		dataRows[0][i+1] = Math.round(parseFloat(dataCompare[i]['pvRatio']) * 5, 2);
		dataRows[1][i+1] = parseFloat(dataCompare[i]['pbRatio']);
		dataRows[2][i+1] = Math.round(parseFloat(dataCompare[i]['peRatio']) / 15, 2);
	}

	data.addRow(dataRows[0]);
	data.addRow(dataRows[1]);
	data.addRow(dataRows[2]);


	// Set chart options
	var options = {'title':'Values are transformed for ease of comparison',
					//hAxis: {title: 'Ticker', titleTextStyle: {color: 'red'}},
					//vAxis: {title: "Dollar Amount in Millions", titleTextStyle: {color: 'red'}},
				   'width':1200,
				   'height':350};


	compare_chart.draw(data, options);
}
