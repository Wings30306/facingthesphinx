$(document).ready(function() {
  queue()
    .defer(d3.json, "data/score.json")
    .await(charts);

  function charts(error, scoreData) {
    let ndx = crossfilter(scoreData);

    showTable(ndx);

    dc.renderAll();
  }

  function showTable(ndx) {
    var dim = ndx.dimension(dc.pluck("score"));
    dc.dataTable("#leaderboard")
      .dimension(dim)
      .group(function(d) {
        return "";
      })
      .columns(["name", "score"])
      .size(10)
      .sortBy(function(d) {
        return d.score;
      })
      .order(d3.descending)
      .transitionDuration(0.5);
  }
});