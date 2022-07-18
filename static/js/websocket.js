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



// load data to leaderboard

const rankingsBody = document.querySelector("#rankings > tbody");

function loadRankings () {
    const request = new XMLHttpRequest();

    request.open("get", "https://codepen.io/imisterk/pen/MLgwOa.js");
    request.onload = () => {
        try {
            const json = JSON.parse(request.responseText);
            populateRankings(json);
        } catch (e) {
            console.warn("Could not load Player Rankings! :(");
        }
    };

    request.send();
}

function populateRankings (json) {
    // Populate Leaderboard
    json.forEach((row) => {
        const tr = document.createElement("tr");

        row.forEach((cell) => {
            const td = document.createElement("td");
            td.textContent = cell;
            tr.appendChild(td);
        });

        rankingsBody.appendChild(tr);
    });
}

json = [
    [
        1,
        "Nihilum",
        "United States",
        "Hydramist",
        "Reckful",
        "33",
        "2390"
    ],
    [
        2,
        "SK Gaming",
        "United Kingdom",
        "Ninja",
        "SmashBr0",
        "32",
        "2243"
    ],
    [
        3,
        "Fnatic",
        "Sweden",
        "Snackbar",
        "Gamer1337",
        "33",
        "2121"
    ],
    [
        4,
        "Dignitas",
        "Finland",
        "Swifty",
        "allan-snackbar",
        "30",
        "2108"
    ],
    [
        5,
        "Phase",
        "Austria",
        "Mercader",
        "Athenelol",
        "28",
        "2048"
    ],
    [
        6,
        "Nihilum",
        "United States",
        "Athelete",
        "Shad0w",
        "24",
        "2390"
    ],
    [
        7,
        "SK Gaming",
        "United Kingdom",
        "eNergY",
        "Kungen",
        "23",
        "2243"
    ],
    [
        8,
        "Fnatic",
        "Sweden",
        "Shwahla",
        "Elitist",
        "26",
        "2121"
    ],
    [
        9,
        "Dignitas",
        "Finland",
        "Ghostcrawler",
        "Metzen",
        "19",
        "2108"
    ],
    [
        10,
        "Phase",
        "Austria",
        "RMP",
        "SpawN",
        "17",
        "2048"
    ]
]

populateRankings(json);
