# midi-cast-py

A RESTful API server for sending HTTP requests to a MIDI device

## Setup 

1. Clone The Repo
>  git clone git@github.com:mastergray/midi-cast-py.git && cd midi-cast-py

2. Setup a virtual enviroment

> /usr/bin/python3.11 -m venv venv

3. Start the virtual enviroment

> source venv/bin/activate

4. Install dependencies

> pip install -r requirements.txt


## API Routes

| Method | Route        | Params                                                    | Description                      | Response | 
|--------|--------------|-----------------------------------------------------------|----------------------------------|----------|
| POST   | /on/:channel | ```{note:STRING, gate:INT\|VOID, velocity:INT\VOID}```    | Sends **NOTE_ON** message to channel | ```{"_channel": INT, "_noteValue": INT, "_noteName": STRING, "_gate": INT\|VOID, "_velocity": INT, "_msgType": "note_on"}```|
| POST   | /off/:channel | ```{note:STRING, gate:INT\|VOID, velocity:INT\VOID}```    | Sends **NOTE_OFF** message to channel | ```{"_channel": INT, "_noteValue": INT, "_noteName": STRING, "_gate": INT\|VOID, "_velocity": INT, "_msgType": "note_off"}```|




### Notes
- An unset `gate` param means the action will continue until it's stopped
- Channels are always `channelNumber - 1` **EXCEPT** for API Routes - there the channel number maps to the expected value. This is because list indexs start at _0_, but I thought it would be easier to use the expected channel number for the route: this is why the channel in the response doesn't match the channel of the route. 

