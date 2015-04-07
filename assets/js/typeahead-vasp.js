var stocks = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('ticker'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  limit: 10,
  prefetch: {
	ttl: 1,
    // url points to a json file that contains an array of stock names, see
    // https://github.com/twitter/typeahead.js/blob/gh-pages/data/countries.json
    url: '/StockTickersJson',
    // the json file contains an array of strings, but the Bloodhound
    // suggestion engine expects JavaScript objects so this converts all of
    // those strings
	
    //filter: function(list) {
    //  return $.map(list, function(stock) { return { val: stock }; });
    //}
  }
});

// kicks off the loading/processing of `local` and `prefetch`
stocks.initialize();

function onSelected($e, datum) {
    //console.log('selected');
    //console.log(datum);
}


// passing in `null` for the `options` arguments will result in the default
// options being used
$('#custom-templates .typeahead').typeahead(null, {
  name: 'stocks',
  displayKey: 'ticker',
  valueKey: 'ticker',
  // `ttAdapter` wraps the suggestion engine in an adapter that
  // is compatible with the typeahead jQuery plugin
  source: stocks.ttAdapter(),
  templates: {
			   suggestion: Handlebars.compile('<p><strong>{{ticker}}</strong> – {{name}}</p>')
		     }
}).on('typeahead:opened', onSelected);