(function(){
    "use strict";
    var transductor_data;
    google.charts.load('current', {'packages':['corechart']});
    google.charts.load('current', {'packages':['corechart', 'controls']});

    $("#select_transductor_btn").click(function(){
        var transductor_id = $("#selectTransductor option:selected").val();
        if(transductor_id != ""){
          $.ajax({
              url: "/reports/get_data_by_transductor/" + transductor_id,
              type: "GET",
              success: function(response){
                  transductor_data = response;
                  console.log(transductor_data);
                  draw_initial_chart();
              }
          })
        }
    });
    $("#current_chart").click(function(){
      var data = [[
          "Date", "current_a", "current_b", "current_c",
      ]];
      if(transductor_data != null){
          for(var i = 0; i < transductor_data.length; i++){
            var measurements = transductor_data[i].fields;
            data.push([
              parseDate(measurements.collection_date),
              measurements.current_a,
              measurements.current_b,
              measurements.current_c,
            ])
          }
          draw_base_chart(data);
      }
      else {
          alert('Chose a transductor and click select before you try the Current Filter.');
      }
    })

    function draw_base_chart(data){
      data = google.visualization.arrayToDataTable(data);

      var options = {
          title: 'Company Performance',
          curveType: 'function',
          legend: { position: 'bottom' }
        };


        var dashboard = new google.visualization.Dashboard(
                document.getElementById('dashboard_div'));


        // Create a range slider, passing some options
        var RangeSlider = new google.visualization.ControlWrapper({
           'controlType': 'ChartRangeFilter',
           'containerId': document.getElementById('filter_div'),
           'options': {
             'filterColumnLabel': 'Date',
             'title': 'Time Filter',
             'ui': {
                 'label': 'Time Filter',
             }
            }
        });

        // Create a pie chart, passing some options
          var chart = new google.visualization.ChartWrapper({
            'chartType': 'LineChart',
            'containerId': document.getElementById('curve_chart'),
            'options': {
              'width': 900,
              'height': 400,
              'title': 'Company Performance',
              'legend': { position: 'bottom' },
              curveType: 'function'

            },
          });

        var columnsTable = new google.visualization.DataTable();
        columnsTable.addColumn('number', 'colIndex');
        columnsTable.addColumn('string', 'colLabel');
        var initState= {selectedValues: []};
        // put the columns into this data table (skip column 0)
        for (var i = 1; i < data.getNumberOfColumns(); i++) {
            columnsTable.addRow([i, data.getColumnLabel(i)]);
            initState.selectedValues.push(data.getColumnLabel(i));
        }

          var columnFilter = new google.visualization.ControlWrapper({
            'controlType': 'CategoryFilter',
            'containerId': document.getElementById('column_filter'),
            'dataTable': columnsTable,
            'options': {
                'filterColumnLabel': 'colLabel',
                'ui': {
                    'label': 'Data Filter',
                    'allowTyping': false,
                    'allowMultiple': true,
                    labelStacking: 'horizontal'
                }
            },
            'state': initState
        });

        google.visualization.events.addListener(columnFilter, 'statechange', function () {
             var state = columnFilter.getState();
             var row;
             var columnIndices = [0];
             for (var i = 0; i < state.selectedValues.length; i++) {
                 row = columnsTable.getFilteredRows([{column: 1, value: state.selectedValues[i]}])[0];
                 columnIndices.push(columnsTable.getValue(row, 0));
             }
             // sort the indices into their original order
             columnIndices.sort(function (a, b) {
                 return (a - b);
             });

             if(columnIndices != 0){
                chart.setView({columns: columnIndices}-1);
                RangeSlider.setView({columns: columnIndices});
                dashboard.bind(RangeSlider,chart);
                dashboard.draw(data, options);
            }
        });

          columnFilter.draw();
          dashboard.bind(RangeSlider,chart);
          dashboard.draw(data, options);
    }

    function draw_initial_chart(){
      var data = [
        ["Date",
        "Active power A", "Active power B", "Active power C",
        "Apparent power A", "Apparent power B", "Apparent power C",
        "Current A", "Current B", "Current C",
        "Reactive Power A", "Reactive Power B", "Reactive Power C",
        "Voltage A", "Voltage B", "Voltage C"
        ]
      ];

      for(var i = 0; i < transductor_data.length; i++){
        var measurements = transductor_data[i].fields;
        data.push([
          parseDate(measurements.collection_date),
          measurements.voltage_a,
          measurements.voltage_b,
          measurements.voltage_c,
          measurements.current_a,
          measurements.current_b,
          measurements.current_c,
          measurements.active_power_a,
          measurements.active_power_b,
          measurements.active_power_c,
          measurements.reactive_power_a,
          measurements.reactive_power_b,
          measurements.reactive_power_c,
          measurements.apparent_power_a,
          measurements.apparent_power_b,
          measurements.apparent_power_c,
        ])
      }
      draw_base_chart(data);
    }


    function parseDate(date_string){
      var date = new Date(date_string);

      return new Date(date.getMonth()+"/"+date.getDate()+"/"+date.getFullYear());
    }

})();
