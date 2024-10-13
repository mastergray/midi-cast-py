# midi-cast-py

A RESTful API server for sending HTTP requests to a MIDI device

## API Routes

| Method | Route        | Params                                                    | Description                      | Response | 
|--------|--------------|-----------------------------------------------------------|----------------------------------|----------|
| POST   | /on/:channel | ```{note:STRING, gate:INT\|VOID, velocity:INT\VOID}```    | Sends **NOTE_ON** message to channel | ```{"_channel": INT, "_noteValue": INT, "_noteName": STRING, "_gate": INT\|VOID, "_velocity": INT, "_msgType": "note_on"}```|
| POST   | /off/:channel | ```{note:STRING, gate:INT\|VOID, velocity:INT\VOID}```    | Sends **NOTE_OFF** message to channel | ```{"_channel": INT, "_noteValue": INT, "_noteName": STRING, "_gate": INT\|VOID, "_velocity": INT, "_msgType": "note_off"}```|




### Notes
- An unset `gate` param means the action will continue until it's stopped
- Channels are always `channelNumber - 1` **EXCEPT** for API Routes - there the channel number maps to the expected value. This is because list indexs start at _0_, but I thought it would be easier to use the expected channel number for the route: this is why the channel in the response doesn't match the channel of the route. 

