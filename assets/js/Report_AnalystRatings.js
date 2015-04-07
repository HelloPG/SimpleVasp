
$(document).ready(function () {
	$("#vt_all").prop("checked",true);
	$("#rc_all").prop("checked",true);
	fetchAR();
});

function fetchAR() {
  var fetchUrl = "/Reports/arDataFetch";
  var vt, rc;

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

  if($('#rc_all').is(':checked')){
	rc = 'ALL';
  }
  else if($('#rc_U').is(':checked')){
	rc = 'U';
  }
  else if($('#rc_D').is(':checked')){
	rc = 'D';
  }
  else if($('#rc_I').is(':checked')){
	rc = 'I';
  }

  $.ajax({
	url: fetchUrl,
	dataType: 'json',
	data: JSON.stringify({ 'vt': vt, 'rc': rc}),
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
    data.addColumn('string', 'Analyst');
	data.addColumn('string', 'Old Rating');
	data.addColumn('string', 'New Rating');
	data.addColumn('number', '(iValue-Price)/Price');
	data.addColumn('number', 'Price/Earnings');
	data.addColumn('number', 'Price/Book Value');

	totalRows = rData.length;

	for (i=0; i<totalRows; i++)
	{
		data.addRow([rData[i].date, rData[i].ticker, rData[i].name,
		 			 rData[i].analyst, rData[i].oldRating, rData[i].newRating,
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

