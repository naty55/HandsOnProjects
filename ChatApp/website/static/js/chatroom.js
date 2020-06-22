$(function() {
    console.log("Ajax acting");
    $('#send').bind('click', send_message);
});

function send_message(){
    let message = $('input[name="message"]').val();
    $('input[name="message"]').val(""); // set the value to empty for writing new message
    console.log("sending " + message);
    $.ajax({
        url: '/send',
        method: 'post',
        data: JSON.stringify({ "message" : message }),
        contentType: 'application/json'
        });

}

var msgs = [];     // store all msgs
var flag = false; // if set to true it will stop the update function


function update(){
  // update client every 4 secs and check for new messages

  fetch('/update', {credentials: "include"}).then(function(response) {
  return response.json();}).then(log);

  if (flag){
  // if flag set to true the stop updating
  // it happens because of the client sent disconnect request
  return null;
  }

  setTimeout(update, 2000);

  function log(myJson){
  // take all new messages and show them on the screen
  let new_messages =  myJson["messages"]
  let info = myJson['info']

  // update
  $("#people").text(info["count"])

  msgs = msgs.concat(new_messages)

  if (new_messages == "Not connected"){
     console.log("you are not connected try to reconnect")
     flag = true
     return null;
  }
  for (i in new_messages){
      if (new_messages[i] == '{quit}'){
          flag = true
          }
      $("#messages").append("<p>" + new_messages[i] + "</p>")

      }
  }
}

update()
