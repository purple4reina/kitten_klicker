var host = window.location.host;
var proto = (window.location.protocol == "https:") ? "wss://" : "ws://"
var ws = new WebSocket(proto + host + "/ws");

var count = 0;
var prod = 0;
var countElement;
var prodElement;

document.addEventListener("DOMContentLoaded", function(e) {
    countElement = document.getElementById('count');
    prodElement = document.getElementById('prod');
});

ws.onmessage = function (e) {
    var value = JSON.parse(e.data);

    count = value.kitten_count;
    countElement.innerText = value.kitten_count.toLocaleString();

    prod = value.prod_per_sec;
    prodElement.innerText = value.prod_per_sec.toLocaleString();
}

ws.onopen = function (e) {
    var storeItems = document.getElementsByClassName('storeItem');
    for(var i = 0; i < storeItems.length; i++) {
        storeItems.item(i).onclick = function (e) {
            ws.send(this.id);
        }
    };

    var kittenImage = document.getElementById("kittenImage");
    var origSize = kittenImage.style.width;
    kittenImage.onmousedown = function (e) {
        this.style.width = "49%";
        ws.send('click');
    }
    kittenImage.onmouseup = function(e) {
        this.style.width = origSize;
    }

    // Simulate continuous updating of the kitten count. When messages are
    // receved from the server, those will take precedence.

    var cycleTime = 0.1;

    function sleep(sec) {
        return new Promise(resolve => setTimeout(resolve, sec * 1000));
    }

    function update() {
        count = count + Math.floor(prod * cycleTime);
        countElement.innerText = count.toLocaleString();
    }

    async function updateKittenCount() {
        while (true) {
            await sleep(cycleTime);
            update();
        }
    };
    updateKittenCount();
}
