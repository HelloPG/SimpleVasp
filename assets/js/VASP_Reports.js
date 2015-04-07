
$(document).ready(function () {
	$('#uvReport').select();
	$('#uvReport').click();
});

$('#uvReport').on('click', function (e) {
	reportDataFetch('uv');
})

$('#ovReport').on('click', function (e) {
	reportDataFetch('ov');
})

$('#fvReport').on('click', function (e) {
	reportDataFetch('fv');
})

$('#ratingsReport').on('click', function (e) {
	reportDataFetch('ratings');
})

$('#uvRatingsReport').on('click', function (e) {
	reportDataFetch('uvRatings');
})

$('#ovRatingsReport').on('click', function (e) {
	reportDataFetch('ovRatings');
})

function reportDataFetch(reportType) {
  var fetchUrl = '';
  
  if (reportType == 'uv')
  {
	fetchUrl = "/Reports/" + reportType + "ReportDataFetch";
	$('#ReportName').html("UnderValued Stocks");
  }
  else if (reportType == 'ov')
  {
  	fetchUrl = "/Reports/" + reportType + "ReportDataFetch";
	$('#ReportName').html("OverValued Stocks");
  }
  else if (reportType == 'fv')
  {
  	fetchUrl = "/Reports/" + reportType + "ReportDataFetch";
	$('#ReportName').html("FairValued Stocks");
  }
  else if (reportType == 'ratings')
  {
  	fetchUrl = "/Reports/" + reportType + "ReportDataFetch" + "?Type=base";
	$('#ReportName').html("Analyst Rating Changes - in last 10 days");
  }
  else if (reportType == 'uvRatings')
  {
  	fetchUrl = "/Reports/ratingsReportDataFetch?Type=uv";
	$('#ReportName').html("Analyst Upgrades for UnderValued Stocks - in last 10 days");
  }
  else if (reportType == 'ovRatings')
  {
  	fetchUrl = "/Reports/ratingsReportDataFetch?Type=ov";
	$('#ReportName').html("Analyst Downgrades for Overvalues Stocks - in last 10 days");
  }
  else
	return;
	
  $.ajax({
	url: fetchUrl,
	dataType: 'json',
	success: function (res) 
		{
			if (res.errMessage != null)
			{
				$('#vasp_modal .modal-body').html(res.errMessage);
				$("#vasp_modal").modal('show');
			}
			else
			{
				if (reportType == 'ratings' ||
					reportType == 'uvRatings' ||
					reportType == 'ovRatings')

					ratingsReportDraw(res.data);
				else
					baseReportDraw(res.data);
			}
		},
	error: function(xhr, status, error) 
		{
			//$('#vasp_modal .modal-body').html(xhr.responseText);
			$('#vasp_modal .modal-body').html(error);
			$("#vasp_modal").modal('show');		
		}

	});
}


var report;

var cssClassNames = {
	'headerRow': 'italic-darkblue-font large-font bold-font',
	'tableRow': 'normal-font',
	'oddTableRow': 'normal-font beige-background',
	'selectedTableRow': '',
	'hoverTableRow': '',
	'headerCell': '',
	'tableCell': '',
	'rowNumberCell': ''};
	


function baseReportDraw(rData) {	
	// Create the data table.
	var data = new google.visualization.DataTable();
	
	data.addColumn('string', 'Ticker');
    data.addColumn('string', 'Name');
    data.addColumn('number', 'Price');
	data.addColumn('number', 'iValue');
	data.addColumn('number', 'Price/iValue');
	data.addColumn('number', 'Price/Book Value');
	data.addColumn('number', 'Price/Earnings');
	
	totalRows = rData.length;

	for (i=0; i<100; i++)
	{
		if (rData[i] == null)
			break;
			
		data.addRow([rData[i].ticker, rData[i].name, rData[i].price, rData[i].iValue, 
					rData[i].pvRatio, rData[i].pbRatio, rData[i].peRatio]); 
	}

	// Set chart options
	var options = {showRowNumber: true,
				   'cssClassNames': cssClassNames,
				   page : 'enable',
				   pageSize: 10,
				   'width':900,
				   'height':250};

	report.draw(data, options);
}

function ratingsReportDraw(rData) {	
	// Create the data table.
	var data = new google.visualization.DataTable();

	data.addColumn('string', 'Date');
	data.addColumn('string', 'Ticker');
    data.addColumn('string', 'Name');
    data.addColumn('number', 'Price');
	data.addColumn('number', 'iValue');
	data.addColumn('number', 'Price/iValue');
	data.addColumn('string', 'Old Rating');
	data.addColumn('string', 'New Rating');
	data.addColumn('string', 'Analyst');
	
	totalRows = rData.length;

	for (i=0; i<totalRows; i++)
	{
		data.addRow([rData[i].date, rData[i].ticker, rData[i].name, parseFloat(rData[i].price), parseFloat(rData[i].iValue),
					parseFloat(rData[i].pvRatio), rData[i].oldRating, rData[i].newRating, rData[i].analyst]); 
	}

	// Set chart options
	var options = {showRowNumber: true,
				   'cssClassNames': cssClassNames,
				   page : 'enable',
				   pageSize: 10,
				   'width':900,
				   'height':250};

	report.draw(data, options);
}