
$(document).ready(function () {
	$("#vt_uv").prop("checked",true);
	fetchTop();
});

function fetchTop() {
  var fetchUrl = "/Reports/topDataFetch";
  var vt;

  // Get criteria parameters
  if($('#vt_uv').is(':checked')){
	vt = 'UV';
  }
  else if($('#vt_ov').is(':checked')){
	vt = 'OV';
  }


  $.ajax({
	url: fetchUrl,
	dataType: 'json',
	data: JSON.stringify({ 'vt': vt}),
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

	data.addColumn('string', 'Ticker');
    data.addColumn('string', 'Name');
    data.addColumn('number', 'Price');
	data.addColumn('number', 'iValue');
	data.addColumn('number', '(iValue-Price)/Price');
	data.addColumn('number', 'Price/Earnings');
	data.addColumn('number', 'Price/Book Value');

	totalRows = rData.length;

	for (i=0; i<100; i++)
	{
		if (rData[i] == null)
			break;

		data.addRow([rData[i].ticker, rData[i].name, rData[i].price, rData[i].iValue,
					rData[i].ivPrem, rData[i].peRatio, rData[i].pbRatio]);
	}

	// Set chart options
	var options = {showRowNumber: true,
				   'cssClassNames': cssClassNames,
				   page : 'enable',
				   pageSize: 10,
				   'width':1000,
				   'height':250};

	report.draw(data, options);
}

