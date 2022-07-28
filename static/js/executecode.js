function getCookie(name) {
    if (!document.cookie) {
      return null;
    }
  
    const xsrfCookies = document.cookie.split(';')
      .map(c => c.trim())
      .filter(c => c.startsWith(name + '='));
  
    if (xsrfCookies.length === 0) {
      return null;
    }
    return decodeURIComponent(xsrfCookies[0].split('=')[1]);
  }


async function executecode(code,input,language,problem="") {
    toggle_block_btns();
    let response = await fetch('/executecode', {
        credentials: 'include',
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('X-CSRFToken')
        },
        body: JSON.stringify({
            "language": language,
            "code": code,
            "input": input,
            "problem": problem
        })
    })
    if (response.ok) {
        let json = await response.json();
        let task_id = json["task_id"]
        id = setInterval(track_task,4000,task_id);
    } else {
        alert("HTTP-Error: " + response.status);
    }
}


async function track_task(task_id,def=true){
    let response = await fetch('/celery-progress/'+task_id, {
        credentials: 'include',
        method: 'GET',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    })
    if (response.ok) {
        let json = await response.json();
        if(json['state']!='PENDING'){
            try{
                clearInterval(id);
            }catch(err){
            }
            try{
                clearInterval(idsubmit);
            }catch(err){

            }
            
            if(json["state"])
                display_on_page(json["result"],def);
            else
                alert('Error: 500 Something went wrong...')
        }
    } else {
        alert("HTTP-Error: " + response.status);
    }
}


function display_on_page(data,def=true){
    try{
        document.getElementById('outputwndow').style.display = 'block';
    }catch(err){
    }

    try{
        console.log(data);
        var data = JSON.parse(data);
    }catch(err){
        document.getElementById('outputwndow').innerText = "Your code didn't run within time limit.";
        if(def)
            toggle_block_btns();
        else{
            showSubmitInfo(data);
            toggle_block_btns_submit();
        }
        return;
    }

    if(def)
        toggle_block_btns();
    else
        toggle_block_btns_submit();

    if(data['success']){
        document.getElementById('outputwndow').innerText = data['output'];
    }
    else{
        document.getElementById('outputwndow').innerText = data['error'];
    }
}


function showSubmitInfo(data){
    var elm = document.getElementById('outputwndow');
    if(data=='success'){
        elm.innerText = 'Congratulations! All test cased passed.';
        elm.style.fontSize = '20px';
        elm.style.color = 'green';
        elm.style.fontWeight = 600;
    }else{
        elm.innerText = 'Sorry! one or more test case failed.';
        elm.style.fontSize = '20px';
        elm.style.color = 'crimson';
        elm.style.fontWeight = 600;
    }
}



function toggle_block_btns(){
    var btn = document.getElementById('run_code_btn');
    if(btn.disabled){
        btn.disabled = false;
        btn.style.cursor = 'pointer';
    }else{
        btn.disabled = true;
        btn.style.cursor = 'auto';
    }
}


function toggle_block_btns_submit(){
    var btn = document.getElementById('submit_code');
    if(btn.disabled){
        btn.disabled = false;
        btn.style.cursor = 'pointer';
    }else{
        btn.disabled = true;
        btn.style.cursor = 'auto';
    }
}


async function submitcode(code,language,problem="",challenge=""){
    toggle_block_btns_submit();
    let response = await fetch('/submitcode', {
        credentials: 'include',
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('X-CSRFToken')
        },
        body: JSON.stringify({
            "language": language,
            "code": code,
            "problem_id": problem,
            "challenge": challenge
        })
    })
    if (response.ok) {
        let json = await response.json();
        console.log(json["message"]);
        let task_id = json["task_id"]
        if(task_id===undefined||task_id===NaN){
            toggle_block_btns_submit()
            return
        }
        idsubmit = setInterval(track_task,4000,task_id,false);
    } else {
        alert("HTTP-Error: " + response.status);
    }
}