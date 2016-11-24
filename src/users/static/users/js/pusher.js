Pusher.logToConsole = false;
var id = '{{request.user.id}}'
if(id != 'None') {
  var pusher = new Pusher('01346f7690ac693e7adb', {
    encrypted: true
  });
  var channel = pusher.subscribe('notification_'+'{{request.user.id}}');
  channel.bind('create', function(data) {
    var notification_name = 'notification_'+ data[0].pk;
    console.log(data);
    $("#allert-container").append(
      getAlertType(data[0], notification_name)
    );
    $("#" + notification_name).click(function() {
      $("[name=" + notification_name +"]").remove();
    });
  });
  function getAlertType(notification, notification_name) {
    var element = "";
    switch (notification.fields.priority) {
      case 1:
      element = '<div class="alert alert-info" name="' + notification_name + '"> '+
      '   <a href="#" class="close" data-dismiss="alert" id="' + notification_name +'" aria-label="close">&times;</a> '+
      notification.fields.description +
      '</div>'
      break;
      case 2:
      element = '<div class="alert alert-success" name="' + notification_name + '"> '+
      '   <a href="#" class="close" data-dismiss="alert" id="' + notification_name +'" aria-label="close">&times;</a> '+
      '   <strong>Sucesso: </strong> '+ notification.fields.description +
      '</div>'
      break;
      case 3:
      element = '<div class="alert alert-warning" name="' + notification_name + '"> '+
      '   <a href="#" class="close" data-dismiss="alert" id="' + notification_name +'" aria-label="close">&times;</a> '+
      '   <strong>Alerta: </strong> '+ notification.fields.description +
      '</div>'
      break;
      default:
      element +=  '<div class="alert alert-danger" name="' + notification_name + '"> '+
      '   <a href="#" class="close" data-dismiss="alert" id="' + notification_name +'" aria-label="close">&times;</a> '+
      '   <p><strong>Perigo: </strong> '+ notification.fields.description + "</p>";
      if(notification.fields.local && notification.fields.local != "") {
        element +="<p><strong>Local:</strong> " + notification.fields.local + "</p>";
      }

      break;
    }
    return element;
  }
}
