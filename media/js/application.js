$(document).ready(function(){
  
  if(!sortPlease) return;
  // Custom CSS on highlighted column
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
  // Custom parser for comma-delimited numbers
  $.tablesorter.addParser({
    id: "fancyNumber",
    is: function(s) {
      return /^[0-9]?[0-9,\.]*$/.test(s);
    },
    format: function(s) {
      return jQuery.tablesorter.formatFloat( s.replace(/,/g,'') );
    },
    type: "numeric"
  });

  //initialize the table
  var fu = $('#table_fu');
  var table = window.table = $('#data', fu)
    .tablesorter({ widgets: ['columnHighlight'], sortList: sortOrder })
    .tablesorterPager({ container: $("#pager", fu), size: perPage, positionFixed: false })
    .tablesorterMultiPageFilter({ filterSelector: $("#filter input", fu) });
  // share buttons
  $(".share_button").shareify({
    'image_dir': '/media/img/'
  }).hover(function() {
    $(this).css({background: '#555'});
  },function(){
    $(this).css({background: '#333'});
  });


});
