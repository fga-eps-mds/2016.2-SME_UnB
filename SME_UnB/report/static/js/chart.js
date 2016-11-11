(function(){
    "use strict";
    var transductor_data;
    google.charts.load('current', {'packages':['corechart']});

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
          "date", "current_a", "current_b", "current_c",
      ]];

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
    })

    function draw_base_chart(data){
      data = google.visualization.arrayToDataTable(data);

      var options = {
          title: 'Company Performance',
          curveType: 'function',
          legend: { position: 'bottom' }
        };

        var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

        chart.draw(data, options);
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
      return date.getDate() + "/" + date.getMonth() + "/" + date.getFullYear();
    }

})();
