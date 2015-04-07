function clearResultTable()
{
  var ht_result = $('#Result').handsontable('getInstance');
  var blankResultData = [
		{id:"1", rowName:"<b>Value on year 6 of next 15 years of FCFs<sup>1</sup></b>", formula:"FCF<sub>5</sub>&times;[1-(1+COE)<sup>-15</sup>]&divide;COE", value:""},
		{id:"2", rowName:"<b>Sum of all future  Discounted FCFs<sup>2</sup></b>", formula:" 	&#931;( FCF<sub>n</sub>/(1+COE)<sup>n</sup> )", value:""},
		{id:"3", rowName:"<b>Number of Shares</b>", formula:"in millions", value:""},	
		{id:"", rowName:"", formula:"", value:""},			
		{id:"", rowName:"<b>Share Intrinsic Value (iValue)</b>", formula:"Sum of all future  Discounted FCFs(2) / Number of Shares(3)", value:""},
		{id:"", rowName:"<b>Share Market Value</b>", formula:"", "value":""},	

	];
	
	ht_result.loadData(blankResultData);
}


function renderResult()
{
  var resultData = [
		{id:"1", rowName:"<b>Value on year 6 of next 15 years of FCFs<sup>1</sup></b>", formula:"FCF<sub>5</sub>&times;[1-(1+COE)<sup>-15</sup>]&divide;COE", value:""},
		{id:"2", rowName:"<b>Sum of all future  Discounted FCFs<sup>2</sup></b>", formula:" 	&#931;( FCFE<sub>n</sub> &divide; (1+COE)<sup>n</sup> )", value:""},
		{id:"3", rowName:"<b>Number of Shares</b>", formula:" in millions", value:""},	
		{id:"", rowName:"", formula:"", value:""},	
		{id:"", rowName:"<b>Share Intrinsic Value (iValue)</b>", formula:"Sum of all future  Discounted FCFs(2)<br />&divide;<br />Number of Shares(3)", value:""},
		{id:"", rowName:"<b>Share Market Value</b>", "formula":"", "value":""},	
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
	  var escaped = Handsontable.helper.stringify(value);
	  td.innerHTML = escaped;
	};
	
  $('#Result').handsontable({
    data: resultData,
    minSpareRows: 0,

    contextMenu: false,
	
	rowHeights: [5, 5, 5, 5],
	colWidths: [25, 350, 400, 150],

	colHeaders: ["", "Variable", "Formula", "Value"],
	
	columns: [
				{data: "id", renderer: labelRenderer, readOnly: true},
				{data: "rowName", renderer: labelRenderer, className: "htLeft", readOnly: true},
				{data: "formula", renderer: fieldRenderer, className: "htCenter", readOnly: true},
				{data: "value",  renderer: fieldRenderer, type: 'numeric', readOnly: true},
			 ],

  });
}

$(document).ready(function () { 
});