var margin = {top: 20, right: 100, bottom: 30, left: 100},
    width = window.innerWidth - 20 - margin.left - margin.right,
    height = window.innerHeight - 20- margin.top - margin.bottom;

var x = d3.time.scale()
    .range([0, width]);

var ly = d3.scale.linear()
    .range([height, 0]);
var ry = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var lyAxis = d3.svg.axis()
    .scale(ly)
    .orient("left");
var ryAxis = d3.svg.axis()
    .scale(ry)
    .orient("right");

var line_mb = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return ly(d.mb); });
var line_mins = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return ry(d.min); });

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

var parseDate = d3.time.format("%d-%b-%y").parse,
    bisectDate = d3.bisector(function(d) { return d.date; }).left,
    formatValue = d3.format(",.2f"),
    formatData = function(d) { return d.date.toLocaleString() + ": " + d.mb + "mb, " + d.min + " minutes"; };

var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

d3.csv("usage.csv", function(error, data) {
  data.forEach(function(d) {
    d.date = new Date(d.time * 1000);
    d.mb = +d.mb;
    d.min = +d.min;
    delete d.time;
  });

  x.domain(d3.extent(data, function(d) { return d.date; }));
  ly.domain([0, d3.extent(data, function(d) { return d.mb; })[1]]);
  ry.domain([0, d3.extent(data, function(d) { return d.min; })[1]]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(lyAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("x", -50)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .attr('class', 'mb')
      .text("Megabytes Left");

  svg.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(" + width + " ,0)")
      .call(ryAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -12)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .attr('class', 'mins')
      .text("Minutes Left");

  svg.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("class", "mb")
      .attr("d", line_mb);
  svg.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("class", "mins")
      .attr("d", line_mins);

  var focus = svg.append("g")
      .attr("class", "focus")
      .style("display", "none");

  focus.append("circle")
      .attr("r", 4.5);

  focus.append("text")
      .attr("x", 9)
      .attr("dy", ".35em");

  svg.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .on("mouseover", function() { focus.style("display", null); })
      .on("mouseout", function() { focus.style("display", "none"); })
      .on("mousemove", mousemove);

  function mousemove() {
    var x0 = x.invert(d3.mouse(this)[0]),
        i = bisectDate(data, x0, 1),
        d0 = data[i - 1],
        d1 = data[i],
        d = x0 - d0.date > d1.date - x0 ? d1 : d0;
    focus.attr("transform", "translate(" + x(d.date) + "," + ly(d.mb) + ")");
    focus.select("text").text(formatData(d));
  }
});
