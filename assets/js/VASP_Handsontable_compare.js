function clearCompareTable()
{
  var ht_compare = $('#Compare').handsontable('getInstance');
  ht_compare.loadData([]);
}


function renderCompare()
{
  var compareData = []

	var blackRenderer = function (instance, td, row, col, prop, value, cellProperties) {
	  Handsontable.renderers.TextRenderer.apply(this, arguments);
	  $(td).css({
		background: 'black',
		color: 'white'
	  });
	};
	
  $('#Compare').handsontable({
    data: compareData,
    minSpareRows: 0,

    contextMenu: false,
	rowHeaders: true,
  
	colWidths: [70, 200, 80, 80, 125, 125, 125],
	colHeaders: ["Ticker", "Name", "Price", "iValue", "(iValue-Price)/Price", "Price/Earnings", "Price/BookValue"],
	columnSorting: true,
	
	columns: [
				{data: "ticker", renderer: blackRenderer, className: "htLeft", readOnly: true},
				{data: "name", renderer: blackRenderer, className: "htLeft", readOnly: true},
				{data: "price", renderer: blackRenderer, className: "htRight", readOnly: true},
				{data: "iValue", renderer: blackRenderer, className: "htRight", readOnly: true},
				{data: "ivPrem", renderer: blackRenderer, className: "htRight", readOnly: true},
				{data: "peRatio", renderer: blackRenderer, className: "htRight", readOnly: true},
				{data: "pbRatio", renderer: blackRenderer, className: "htRight", readOnly: true},
			 ],
	
  });
}

$(document).ready(function () { 
});