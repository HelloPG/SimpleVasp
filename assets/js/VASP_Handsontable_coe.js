
function renderCOE()
{
  var coeData = [
		{id:"1", rowName:"<b>r<sub>f</sub> = 10 year treasury yield</b>", proxy:""},
		{id:"2", rowName:"<b>&#946;<sub>a</sub> (Beta)<sup>*</sup></b>", proxy:""},
		{id:"3", rowName:"<b>r<sub>m</sub> = S&P 500, 1 year return</b>", proxy:""},
		{id:"", rowName:"", proxy:""},
		{id:"", rowName:"<b>r<sub>a</sub> = Cost of Equity</b>", proxy:""},		
	];
 
	// Labels can be html, background - green, text : black
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
	
  $('#CostOfEquity').handsontable({
    data: coeData,
    minSpareRows: 0,
	currentRowClassName: 'currentRow',
	currentColClassName: 'currentCol',
    colHeaders: true,
    contextMenu: false,
	
	rowHeights: [5, 5, 5, 5, 5],
	colWidths: [25, 250, 85],
	
	colHeaders: ["", "Variable", "Value"],
	
	columns: [
				{data: "id", renderer: labelRenderer, readOnly: true},
				{data: "rowName", renderer: labelRenderer, className: "htLeft", readOnly: true},
				{data: "proxy",  renderer: fieldRenderer, type: 'numeric', readOnly: true},
			 ],
   
	customBorders: [
	],
  });
}

$(document).ready(function () { 
});