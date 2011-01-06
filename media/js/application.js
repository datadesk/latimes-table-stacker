$(document).ready(function(){
  
  if(!sortPlease) return;
  
  $.tablesorter.addWidget({
    id: "columnHighlight",
    format: function(table) {
      if (!this.tds)
        this.tds =  $("td", table.tBodies[0]);
      if (!this.headers)
        this.headers = $("thead th", table);
      this.tds.removeClass("sorted");
      var ascSort = $("th." + table.config.cssAsc);
      var descSort = $("th." + table.config.cssDesc);
      if (ascSort.length)
        index = this.headers.index(ascSort[0]);
      if (descSort.length)
        index = this.headers.index(descSort[0]);
      $("tr td:nth-child(" + (index+1) + ")", table.tBodies[0]).each(function(row){
        $(this).addClass('sorted');
      });
    }
  });
  
  // Number formatting parsing, always difficult in JavaScript
  var NUM_CLEANER = /[$£€\,]/g;
  $.tablesorter.addParser({
    id: "newNumbers",
    is: function(s,table) {
      var newNumber   = s.replace(NUM_CLEANER, "");
      var maybeNumber = parseFloat(s, 10);
      return maybeNumber.toString() === newNumber;
    },
    format: function(s){
      return parseFloat(s, 10);
    },
    type: "numeric"
  });
  
  // Overriding format float to actually test a bit better. If it is a number 
  // already we'll return the number's value, if not we'll call the old parse
  // float from table sorter. 
  var oldFloat = $.tablesorter.formatFloat;
  $.tablesorter.formatFloat = $.tablesorter.formatInt = function(obj){
    return (obj === +obj) || (Object.prototype.toString.call(obj) === '[object Number]') ? obj : oldFloat(obj);
  };
  
  //initialize the table
  var table = window.table = $('#data')
    .tablesorter({ widgets: ['columnHighlight'], sortList: sortOrder })
    .tablesorterPager({ container: $("#pager"), size: perPage, positionFixed: false })
    .tablesorterMultiPageFilter({ filterSelector: $("#filter input") });
});
