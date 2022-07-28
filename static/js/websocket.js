// requires roomName

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/challenge/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data.message);
    document.querySelector('#chat-log').innerHTML += ( "<div class='newmessage'>" + data.message + "</div>");
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#sendmessage_text').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#sendmessage_btn').click();
    }
};

document.querySelector('#sendmessage_btn').onclick = function(e) {
    const messageInputDom = document.querySelector('#sendmessage_text');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    messageInputDom.value = '';
};