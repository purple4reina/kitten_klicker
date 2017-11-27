var host = window.location.host;
var proto = (window.location.protocol == "https:") ? "wss://" : "ws://"
var ws = new WebSocket(proto + host + "/ws");

ws.onmessage = function (e) {
    var value = JSON.parse(e.data);

    var count = document.getElementById('count');
    count.innerText = value.kitten_count;

    var prod = document.getElementById('prod');
    prod.innerText = value.prod_per_sec;
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
}
