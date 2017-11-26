var ws = new WebSocket("ws://" + window.location.host + "/ws");

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

    document.onclick = function (e) {
        ws.send('click');
    }
}
