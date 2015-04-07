
var crowdVaspFlag = true; 

function setCrowdVaspFlag(flag) 
{
  crowdVaspFlag = flag;
}
				
function isNumber(n) 
{
  return !isNaN(parseFloat(n)) && isFinite(n);
}

/*

// When the last year's FCF is set, calculate and set Terminal Perpetual FCF
function setTerminalPerptualFCF(terminalFCF)
{
	var ht_result = $('#Result').handsontable('getInstance');
	var ht_coe = $('#CostOfEquity').handsontable('getInstance');				
	var coe = ht_coe.getDataAtCell(4, 2);

	//var terminalFcfe = Math.round(terminalFCF/(coe/100));
	// FCF stagnated for next 15 years
	var terminalFcfe = Math.round(terminalFCF * 15);
	ht_result.setDataAtCell(0, 3, terminalFcfe);
	
	return terminalFcfe;
}
*/

/*
// When all the 5 FCFs are set, calculate and set
function setSumOfAllDiscountedFCFs(fcfList, terminalFcfe)
{
	var ht_result = $('#Result').handsontable('getInstance');
	var ht_coe = $('#CostOfEquity').handsontable('getInstance');
	
    // Check if FCFs for all the years are specified
	// If not, no need to proceed
	for (j=8; j<=12; j++){
		if (fcfList[j-8] == null)
			return;
	}
	
	var coe = ht_coe.getDataAtCell(4, 2);
	
	var divBase = 1 + (coe/100); 
	
	var div=0, dfcfe=0, dfcfeTotal=0;
	
	for (j=8; j<=12; j++){
		div = Math.pow(divBase, j-7);
		dfcfe = Math.round((fcfList[j-8] / div));
		dfcfeTotal = dfcfeTotal + dfcfe;
	}
		
	// Add Discounted terminal perpatual FCF
	div = Math.pow(divBase, 6);
	
	var dTerminalFcfe = Math.round(terminalFcfe / div);
	dfcfeTotal = dfcfeTotal + dTerminalFcfe;

	// Set 'Sum of Discounted FCFE'
	ht_result.setDataAtCell(1, 3, dfcfeTotal);

	var nbrOfShares = ht_result.getDataAtCell(2, 3);
		
	// Set 'Intrinsic Value'
	if (nbrOfShares == 0 || nbrOfShares == 'N/A')
		ht_result.setDataAtCell(4, 3, 'N/A');
	else
		ht_result.setDataAtCell(4, 3, (dfcfeTotal/nbrOfShares).toFixed(2));
					
}
*/

function renderFCF()				
{
  var fcfData = [
	
	{id:"1", rowName:"<b>Sales</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"YrOverYr % Growth", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
  	
	{id:"2", rowName:"<b>Net Income</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"As % of Sales", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },  

	{id:"3", rowName:"<b>Depreciation</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"As % of Sales", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" }, 
	
	{id:"4", rowName:"<b>Deferred Taxes</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"As % of Sales", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" }, 
	
	{id:"5", rowName:"<b>Other Funds</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"As % of Sales", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" }, 

	{id:"6", rowName:"<b>Capital Expenditure</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"As % of Sales", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" }, 

	{id:"7", rowName:"<b>Working Capital Change</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"As % of Sales", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" }, 

	{id:"", rowName:"", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	{id:"", rowName:"<b>FCF (2 + 3 + 4 + 5 - 6 -7)</b>", n5_:"", n4_:"", n3_:"", n2_:"", n1_:"", PastAvg:"", n1:"", n2:"", n3:"", n4:"", n5:"" },
	
  ];

	// Labels can be html and background green
  	var labelRenderer = function (instance, td, row, col, prop, value, cellProperties) {
	  Handsontable.renderers.TextRenderer.apply(this, arguments);
	  $(td).css({
		background: '#33FF99',
		color: 'black'
	  });
	  var escaped = Handsontable.helper.stringify(value);
	  td.innerHTML = escaped;
	};

	// background - black, text : white
  	var fieldRenderer = function (instance, td, row, col, prop, value, cellProperties) {
	  Handsontable.renderers.TextRenderer.apply(this, arguments);
	  $(td).css({
		color: 'white'
	  });
	};
	
  	var greenRenderer = function (instance, td, row, col, prop, value, cellProperties) {
	  Handsontable.renderers.TextRenderer.apply(this, arguments);
	  $(td).css({
		background: '#33FF99'
	  });
	};
	
	var blackRenderer = function (instance, td, row, col, prop, value, cellProperties) {
	  Handsontable.renderers.TextRenderer.apply(this, arguments);
	  $(td).css({
		background: 'black',
		color: 'white'
	  });
	};
	
	var whiteRenderer = function (instance, td, row, col, prop, value, cellProperties) {
	  Handsontable.renderers.TextRenderer.apply(this, arguments);
	  $(td).css({
		background: 'white',
		color: 'black'
	  });
	};

	
    var grayRenderer = function (instance, td, row, col, prop, value, cellProperties) {
	  Handsontable.renderers.TextRenderer.apply(this, arguments);
	  $(td).css({
		background: 'lightgray'
	  });
	};
	
	/*
    var salesGrowthPercent = function (instance, td, row, col, prop, value, cellProperties) {
	   Handsontable.renderers.TextRenderer.apply(this, arguments);
    
		var prevYrSales, salesGrowth, curYrSales;
    
		// Get Previous year sales
		prevYrSales = instance.getDataAtCell(row, col-1);
		salesGrowth = instance.getDataAtCell(row+1, col);
		curYrSales = (prevYrSales * salesGrowth)/ 100;

		td.innerHTML = curYrSales;
	};
	*/
	
  	var CurYr = 2014;
	
  $('#FreeCashFlow').handsontable({
    data: fcfData,
    minSpareRows: 0,
	currentRowClassName: 'currentRow',
	currentColClassName: 'currentCol',
    colHeaders: true,
    contextMenu: false,
	clickBeginsEditing : true,
	
	/*
	comments: true,
	
    cell: [
		{row: 1, col: 1, comment: "Test comment"},
		{row: 2, col: 2, comment: "Sample"}
    ],
	*/
	
	rowHeights: [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
	colWidths: [25, 180, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 120],
	
	colHeaders: ["", "(Numbers in Millions)", (CurYr-5).toString(), (CurYr-4).toString(), (CurYr-3).toString(), 
											  (CurYr-2).toString(), (CurYr-1).toString(), "5 yr Avg", 
											  (CurYr).toString(), (CurYr+1).toString(), (CurYr+2).toString(),
											  (CurYr+3).toString(), (CurYr+4).toString(), "Forecast", ],
	
	columns: [
				{data: "id", renderer: labelRenderer, readOnly: true},
				{data: "rowName", renderer: labelRenderer, className: "htLeft", readOnly: true},
				{data: "n5_", renderer: fieldRenderer, readOnly: true},
				{data: "n4_", renderer: fieldRenderer, readOnly: true},
				{data: "n3_", renderer: fieldRenderer, readOnly: true},
				{data: "n2_", renderer: fieldRenderer, readOnly: true},
				{data: "n1_", renderer: fieldRenderer, readOnly: true},
				{data: "PastAvg", renderer: labelRenderer, readOnly: true},
				{data: "n1", renderer: fieldRenderer, type: 'numeric', language: 'en'},
				{data: "n2", renderer: fieldRenderer, type: 'numeric', language: 'en'},  //, format: '0,0.00'
				{data: "n3", renderer: fieldRenderer, type: 'numeric', language: 'en'},
				{data: "n4", renderer: fieldRenderer, type: 'numeric', language: 'en'},
				{data: "n5", renderer: fieldRenderer, type: 'numeric', language: 'en'},
				{data: "FM", renderer: labelRenderer, className: "htLeft", readOnly: true},
				/*
				{
				  data: "FM",
				  type: 'dropdown',
				  source: ["Last year value", "Avg of last 5 years", "Analyst Estimates"],
				  renderer: labelRenderer
				},
				*/
			  ],
	
	cells: function (row, col, prop) {				
				if (col > 7 && col < 13){
					if (row==1 || row==3 || row==5 || row==7 || row==9 || row==11 || row==13){
						if (crowdVaspFlag)
							this.renderer = blackRenderer;
						else
							this.renderer = whiteRenderer;
					}
				}
				
				var cellProperties = {};
				
				if (col > 7 && col < 13)
				{
					if (row==0 || row==2 || row==4 || row==6 || row==8 || row==10 || row==12 || row==14 || row==15) 
					{
						cellProperties.readOnly = true;
					}
					else
					{
						if (crowdVaspFlag)
							cellProperties.readOnly = true;
						else
							cellProperties.readOnly = false;
					}
				}
				return cellProperties;
		   },
		   
	beforeChange: function (changes, source) {	
				var ht_fcf = $('#FreeCashFlow').handsontable('getInstance');
				var row = changes[0][0];
				var col = ht_fcf.propToCol(changes[0][1]);

				// If user input anything other than number, reject it.
				if (!isNumber(changes[0][3]))
					return false;
					
				// Before user can enter 'Sales % Growth', previous year 'sales' value should have been entered.
				/*
				if (row==1) 
				{
					if (ht_fcf.getDataAtCell(0, col-1) == '')
					{
						//alert("Please enter previous year sales estimate before entering this value");
						$('#vasp_modal .modal-body').html("<p>Previous year sales estimate needs to be specified before changing this value&hellip;</p>");
						$("#vasp_modal").modal('show');
						return false;
					}
				}
				*/
				
				// Before user can enter 'As % of Sales', 'sales' value should have been entered.
				if (row==3 || row==5 || row==7 || row==9 || row==11 || row==13) 
				{
					if (ht_fcf.getDataAtCell(0, col) == '')
					{
						//alert("Please enter sales estimate before entering this value");
						$('#vasp_modal .modal-body').html("<p>Sales estimate needs to be specified before changing this value&hellip;</p>");
						$("#vasp_modal").modal('show');						
						return false;
					}
				}
		   },
	
	afterChange: function (changes, source) {
				var ht_fcf = $('#FreeCashFlow').handsontable('getInstance');
			    var ht_coe = $('#CostOfEquity').handsontable('getInstance');
			    var ht_result = $('#Result').handsontable('getInstance');
  
				if (source=== 'loadData') {
					return; //don't do anything as this is called when table is loaded
				}
					
				
				var prevYrSales, curYrSales;
				var perSales, salesGrowth, tempValue;
									
				var row = changes[0][0];
				var col = ht_fcf.propToCol(changes[0][1]);
				var oldCellValue = changes[0][2];
				var newCellValue = changes[0][3];
				
				
				// If Sales value changed - cascading effect on rest of the fields
				if (row == 0)
				{
					curYrSales = newCellValue;
											
					// Effect on subsequent years' 'Sales' values
					for (j=col+1; j<=12; j++){
						salesGrowth = ht_fcf.getDataAtCell(1, j);
						
						// If next 'salesGrowth' value is already entered by user 
						if (salesGrowth != '' && salesGrowth != null && salesGrowth !=0){
							tempValue = Math.round(curYrSales * (1 + (salesGrowth/ 100)));
							ht_fcf.setDataAtCell(0, j, tempValue);
						}
					}
				
					// Effect on 'Sales dependent' values
					for (i=2; i<=12; i=i+2){ 
						perSales = ht_fcf.getDataAtCell(i+1, col);
						
						// If 'perSales' value is filled in by user 
						if (perSales != '' && perSales != null && perSales !=0){
							tempValue = (curYrSales * (perSales/ 100)).toFixed(2);
							ht_fcf.setDataAtCell(i, col, tempValue);
						}
					}
				}

				// Sales Growth Percentages - Impacts Row 0 values
				if (row == 1)
				{
					if (col==8)
						prevYrSales = ht_fcf.getDataAtCell(0, 6);
					else
						prevYrSales = ht_fcf.getDataAtCell(0, col-1);
						
					salesGrowth = newCellValue;
					curYrSales = Math.round(prevYrSales * (1 + (salesGrowth/ 100)));

					ht_fcf.setDataAtCell(0, col, curYrSales);					
				}
				
				// ni, Dep, DefTaxes, Other, CapEx, wcDelta - % of Sales values change - Impact on absolute values 
				if (row==3 || row==5 || row==7 || row==9 || row==11 || row==13) 
				{
					perSales = newCellValue;
					curYrSales = ht_fcf.getDataAtCell(0, col);
					tempValue = (curYrSales * (perSales/ 100)).toFixed(2);
					ht_fcf.setDataAtCell(row-1, col, tempValue);
				}
				
				// ni, Dep, DefTaxes, Other, CapEx, wcDelta - Absolute values change - Impact on FCF 
				if (row==2 || row==4 || row==6 || row==8 || row==10 || row==12)
				{
					// Existing values
					var ni = ht_fcf.getDataAtCell(2, col);
					var dep = ht_fcf.getDataAtCell(4, col);
					var defTaxes = ht_fcf.getDataAtCell(6, col);
					var other = ht_fcf.getDataAtCell(8, col);
					var capEx = ht_fcf.getDataAtCell(10, col);
					var wcDelta = ht_fcf.getDataAtCell(12, col);
					
					// New value
					if (row==2)
						ni = newCellValue;
					else if  (row==4)
						dep = newCellValue;
					else if  (row==6)
						defTaxes = newCellValue;
					else if  (row==8)
						other = newCellValue;
					else if  (row==10)
						capEx = newCellValue;
					else if  (row==12)
						wcDelta = newCellValue;	
						
					// If all the values are filled in, add them up for FCF
					if (ni!=null && dep!=null && defTaxes!=null && other!=null && capEx!= null && wcDelta!=null){
						tempValue =  ni + dep + defTaxes + other - capEx - wcDelta;											
						ht_fcf.setDataAtCell(15, col, Math.round(tempValue));
					}
				}
				
				var terminalFcfe=0;

				if (row==15)
				{
					// Terminal Perpetual FCF
					/*
					if (col==12){
						terminalFcfe = setTerminalPerptualFCF(newCellValue);
					}
					*/
					
					// If all the FCFs are set, calculate rest of the results fields
					var fcfs = [null, null, null, null, null]
					
					for(j=8; j<=12; j++){
						// if current column
						if (j == col)
							fcfs[j-8] = newCellValue;
						else
							fcfs[j-8] = ht_fcf.getDataAtCell(15, j);
					}
					
					evalResultData(fcfs);
					
					/*
					if (terminalFcfe==0)
						terminalFcfe = ht_result.getDataAtCell(0, 3);
									
					setSumOfAllDiscountedFCFs(fcfs, terminalFcfe);
					*/
				} // End of 'row=11'
				
			},  // End of 'afterChange'
	
  });
  
}  

function setForecasts(method, rowNum) 
{
	var ht_fcf = $('#FreeCashFlow').handsontable('getInstance');
	var ref = 0;

	// Analyst Estimates
	if (method == 'C')
	{
		// Get current ticker
		var ticker = $("#ticker").val();

		if (ticker==null || ticker=='')
			return;
	
		// Get estimate data for the current ticker
		$.ajax({
				url: "/vasp/LoadAnalystEstimate",
				dataType: 'json',
				data: JSON.stringify({ 'ticker': ticker}),			
				type: 'POST',
				success: function (res) 
					{
						var aeData = res.aeJsonList;
						var aeCount = aeData.length;
						var niPerSales = 0;
						var ni = 0;
						var sales = 0;
						
						/*
						var nbrOfShares = $('#Result').handsontable('getInstance').getDataAtCell(2, 3);
						if (nbrOfShares == 0)
							return;
						*/
						
						for (i=0; i<aeCount; i++)
						{
							year = aeData[i].year;
							ni = aeData[i].ni;
							
							sales = ht_fcf.getDataAtCell(0, 8 + i);
							if (sales == 0)
								sales = 100;

							niPerSales = (ni * 100) / sales;
							//niPerSales = parseFloat(niPerSales).toFixed(2); - if niPerSales is string
							niPerSales = niPerSales.toFixed(2);
							ht_fcf.setDataAtCell(rowNum, 8 + i, niPerSales);

							
						}

					},
				error: function(xhr, status, error) 
					{
						$('#vasp_modal .modal-body').html(error);
						$("#vasp_modal").modal('show');	
					}
			});
			
		return;
	}
	
	// last year's value
	if (method == 'A')
	{
		ref = ht_fcf.getDataAtCell(rowNum, 6);
	}
	// 5 year average
	else if (method == 'B')
	{
		ref = ht_fcf.getDataAtCell(rowNum, 7);
	}	
	else
		return;
		
	// Update forecasts
	for (i=8; i<13; i++)
		ht_fcf.setDataAtCell(rowNum, i, ref);
	
	//$("#FreeCashFlow").handsontable('render');
}


function showGraph()
{

  $.ajax({
	url: "/admin/Graph/Test",
	dataType: 'image/png',
	success: function (res) 
		{
			if (res.errMessage != null)
			{
				$('#vasp_modal .modal-body').html(res.errMessage);
				$("#vasp_modal").modal('show');
			}
			else
			{
				$('#vasp_modal .modal-body').html(res.graph);
				$("#vasp_modal").modal('show');
			}
			
		},
	error: function(xhr, status, error) 
		{
			$('#vasp_modal .modal-body').html(error);
			$("#vasp_modal").modal('show');		
		}

	});
}

$("#FreeCashFlow").on('mousedown', 'input.ForecastMethods', function (event) {
  event.stopPropagation();
});

$("#FreeCashFlow").on('mouseup', 'input.ForecastMethods', function (event) {
	var eventId = event.target.id;

	// Get Forecast Method and row number - fm_A_1
	var params = eventId.split('_');
	
	if (params.length != 3)
		return;
	
	else
	{
		setForecasts (params[1], params[2]);
	}
});



$(document).ready(function () {

});