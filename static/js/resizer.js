TOTAL_WIDTH = window.innerWidth;

document.getElementById('dragMe').addEventListener('mousedown',function(e){
    // Attach the listeners to `document`
    document.addEventListener('mousemove', mouseMoveHandler);
    document.addEventListener('mouseup', mouseUpHandler);
})

document.getElementById('dragMe1').addEventListener('mousedown',function(e){
    // Attach the listeners to `document`
    document.addEventListener('mousemove', mouseMoveHandler1);
    document.addEventListener('mouseup', mouseUpHandler1);
})


function mouseMoveHandler1(e){
    PARTIAL_TOTAL_WIDTH1 = TOTAL_WIDTH;
    x = e.clientX;
    if(x<PARTIAL_TOTAL_WIDTH1){
        document.getElementById('middlepane').style.width = x + "px";
        document.getElementById('rightpane').style.width = PARTIAL_TOTAL_WIDTH1 - x + "px";
    }
}

function mouseUpHandler1(){
    document.removeEventListener('mousemove', mouseMoveHandler1);
    document.removeEventListener('mouseup', mouseUpHandler1);
}

function mouseMoveHandler(e){
    PARTIAL_TOTAL_WIDTH = TOTAL_WIDTH
    console.log(PARTIAL_TOTAL_WIDTH);
    x = e.clientX;
    if(x<PARTIAL_TOTAL_WIDTH){
        document.getElementById('leftpane').style.width = x + "px";
        document.getElementById('middlepane').style.width = PARTIAL_TOTAL_WIDTH - x + "px";
    }
}

function mouseUpHandler() {
    // Remove the handlers of `mousemove` and `mouseup`
    document.removeEventListener('mousemove', mouseMoveHandler);
    document.removeEventListener('mouseup', mouseUpHandler);
};

// max width of first block is (2/3oftotal-50px)
// max width of second block also same
