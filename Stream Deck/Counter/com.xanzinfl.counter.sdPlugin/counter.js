let websocket = null;
let settings = { count: 0, highScore: 0, name: "Counter" };

function connectToStreamDeck(inPort, inUUID, inRegisterEvent) {
    websocket = new WebSocket(`ws://127.0.0.1:${inPort}`);

    websocket.onopen = function () {
        const json = { event: inRegisterEvent, uuid: inUUID };
        websocket.send(JSON.stringify(json));
    };

    websocket.onmessage = function (evt) {
        let jsonObj = JSON.parse(evt.data);

        if (jsonObj.event === "keyDown") {
            settings.count++;
            if (settings.count > settings.highScore) settings.highScore = settings.count;
            updateFile();
            sendUpdate(jsonObj.context);
        } else if (jsonObj.event === "keyUp") {
            // Optional: Handle key release
        }
    };
}

function updateFile() {
    const fs = require('fs');
    fs.writeFileSync('counter.txt', `Current: ${settings.count} - ${settings.name}\nHigh Score: ${settings.highScore}`);
}

function sendUpdate(context) {
    const json = {
        event: "setTitle",
        context: context,
        payload: {
            title: `${settings.count}`
        }
    };
    websocket.send(JSON.stringify(json));
}
