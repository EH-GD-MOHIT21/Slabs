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


async function track_task(task_id){
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
            clearInterval(id);
            if(json["state"])
                display_on_page(json["result"]);
            else
                alert('Error: 500 Something went wrong...')
        }
    } else {
        alert("HTTP-Error: " + response.status);
    }
}


function display_on_page(data){
    try{
        document.getElementById('outputwndow').style.display = 'block';
    }catch(err){
        
    }
    var data = JSON.parse(data);
    toggle_block_btns();
    if(data['success']){
        document.getElementById('code_result_area').innerText = data['output'];
    }
    else{
        document.getElementById('code_result_area').innerText = data['error'];
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