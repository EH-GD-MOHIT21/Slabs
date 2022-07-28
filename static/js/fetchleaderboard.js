const challenge = new URL(document.URL).pathname.split('=')[1];
const nextbtn = document.getElementById('nextbtnleader');
const prevbtn = document.getElementById('prevbtnleader');
var NEXT_URL = undefined;
var PREV_URL = undefined;

nextbtn.addEventListener('click',function(){
    if(NEXT_URL===undefined){
        return;
    }
    leaderboardupdate(NEXT_URL);
})

prevbtn.addEventListener('click',function(){
    if(PREV_URL===undefined){
        return;
    }
    leaderboardupdate(PREV_URL);
})

async function leaderboardupdate(url='/leaderboard?challenge='+challenge){
    let response = await fetch(url, {
        credentials: 'include',
        method: 'GET',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    if (response.ok) {
        let json = await response.json();
        const prevbtnres = response.headers.get('previous')
        const nextbtnres = response.headers.get('next')
        if(prevbtnres=='None'){
            prevbtn.disabled = true;
            prevbtn.style.cursor = 'default';
        }else{
            prevbtn.disabled = false;
            prevbtn.style.cursor = 'pointer';
            PREV_URL = prevbtnres;
        }
        if(nextbtnres=='None'){
            nextbtn.disabled = true;
            nextbtn.style.cursor = 'default';
        }else{
            nextbtn.disabled = false;
            nextbtn.style.cursor = 'pointer';
            NEXT_URL = nextbtnres;
        }
        
        populateRankings(json);
    } else {
        alert("HTTP-Error: " + response.status);
    }
}

// load data to leaderboard

const rankingsBody = document.querySelector("#rankings > tbody");

function populateRankings (json,start_rank,autorank) {
    rankingsBody.innerHTML = ``;
    json.forEach((row,index) => {
        const tr = document.createElement("tr");
        
        const td0 = document.createElement("td");
        td0.textContent = row['rank'];
        tr.appendChild(td0);

        const tdi = document.createElement("td");
        tdi.innerHTML = `<img src=${row['profile_image']} alt='image not found'>`;
        tr.appendChild(tdi);

        const td = document.createElement("td");
        td.textContent = row["first_name"] + " " + row["last_name"];
        tr.appendChild(td);

        const td1 = document.createElement("td");
        td1.textContent = row["username"];
        tr.appendChild(td1);

        const td2 = document.createElement("td");
        td2.textContent = row["country"];
        tr.appendChild(td2);

        const td4 = document.createElement("td");
        td4.textContent = row["user_submissions"].length;
        tr.appendChild(td4);

        const td3 = document.createElement("td");
        td3.textContent = row["avgtime"];
        tr.appendChild(td3);
        
        rankingsBody.appendChild(tr);
    });
}


leaderboardupdate()

document.querySelector('#search-leaderboard').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        leaderboardupdate('/searchleaderboard?challenge='+challenge+'&param='+document.getElementById('search-leaderboard').value);
    }
};

[
    {
        "first_name": "Mohit",
        "last_name": "Satija",
        "username": "mohit",
        "country": "india",
        "profile_image": "/media/others/chayan1.jpg",
        "user_submissions": [
            {
                "id": 2,
                "code": "print(\"Mohit Satija!\")",
                "submission_time": "2022-07-24T08:38:31.031997Z",
                "submission_status": "success",
                "user": 1,
                "problem": 1,
                "challenge": 18
            },
            {
                "id": 4,
                "code": "print(\"Mohit Satija!\")",
                "submission_time": "2022-07-24T09:30:50.734911Z",
                "submission_status": "success",
                "user": 1,
                "problem": 2,
                "challenge": 18
            }
        ],
        "avgtime": "919600.883454"
    },
    {
        "first_name": "Good",
        "last_name": "Game",
        "username": "gg",
        "country": "Bohemia",
        "profile_image": "/media/others/chayan.jpg",
        "user_submissions": [
            {
                "id": 5,
                "code": "passed",
                "submission_time": "2022-07-24T09:34:42.000864Z",
                "submission_status": "success",
                "user": 3,
                "problem": 1,
                "challenge": 18
            },
            {
                "id": 6,
                "code": "qwerty",
                "submission_time": "2022-07-24T09:42:28.389661Z",
                "submission_status": "success",
                "user": 3,
                "problem": 2,
                "challenge": 18
            }
        ],
        "avgtime": "921635.195262"
    }
]