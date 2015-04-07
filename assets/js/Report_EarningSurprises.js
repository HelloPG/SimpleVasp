
$(document).ready(function () {
	$("#vt_all").prop("checked",true);
	$("#st_all").prop("checked",true);
	fetchES();
});

function fetchES() {
  var fetchUrl = "/Reports/esDataFetch";
  var vt, st;

  // Get criteria parameters
  if($('#vt_all').is(':checked')){
	vt = 'ALL';
  }
  else if($('#vt_uv').is(':checked')){
	vt = 'UV';
  }
  else if($('#vt_ov').is(':checked')){
	vt = 'OV';
  }

  if($('#st_all').is(':checked')){
	st = 'ALL';
  }
  else if($('#st_E').is(':checked')){
	st = 'E';
  }
  else if($('#st_M').is(':checked')){
	st = 'M';
  }
  else if($('#st_F').is(':checked')){
	st = 'F';
  }

  $.ajax({
	url: fetchUrl,
	dataType: 'json',
	data: JSON.stringify({ 'vt': vt, 'st': st}),
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
				ReportDraw(res.data);
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
	


function ReportDraw(rData) {
	// Create the data table.
	var data = new google.visualization.DataTable();

	data.addColumn('string', 'Date');
	data.addColumn('string', 'Ticker');
    data.addColumn('string', 'Name');
    data.addColumn('number', 'Estimate');
	data.addColumn('number', 'Actual');
	data.addColumn('number', 'Percent Surprise');
	data.addColumn('number', '(iValue-Price)/Price');
	data.addColumn('number', 'Price/Earnings');
	data.addColumn('number', 'Price/Book Value');
	
	totalRows = rData.length;

	for (i=0; i<100; i++)
	{
		if (rData[i] == null)
			break;
			
		data.addRow([rData[i].date, rData[i].ticker, rData[i].name,
					 parseFloat(rData[i].estimate),
					 parseFloat(rData[i].actual),
					 parseFloat(rData[i].percentSurprise),
					 parseFloat(rData[i].ivPrem),
					 parseFloat(rData[i].peRatio),
					 parseFloat(rData[i].pbRatio)
					]);
	}

	// Set chart options
	var options = {showRowNumber: true,
				   'cssClassNames': cssClassNames,
				   page : 'enable',
				   pageSize: 10,
				   'width':1200,
				   'height':250};

	report.draw(data, options);
}

