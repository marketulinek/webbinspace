function loadChart(chart, endpoint) {
  $.ajax({
    url: endpoint,
    type: 'GET',
    dataType: 'json',
    success: (jsonResponse) => {

      const labels = jsonResponse.data.labels;
      const tooltips = jsonResponse.tooltips;
      const datasets = jsonResponse.data.datasets;

      // Load data into the chart
      chart.data.labels = labels;
      datasets.forEach(dataset => {
        chart.data.datasets.push(dataset);
      });
      chart.options.plugins.tooltip.callbacks.label = function(context) {
        return tooltips[context.dataIndex];
      };

      chart.update();
    },
    error: () => console.log('Failed to fetch chart data from ' + endpoint + '.'),
  });
}