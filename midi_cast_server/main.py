from __future__ import annotations  # Allows forward references in type hints
import typing
if typing.TYPE_CHECKING:
    from midi_queue.main import MIDIQueue                   # Implements queue for sending MIDI messages to

# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from flask import Flask, request, jsonify, Response                     # HTTP Server Framework
from midi_queue_vizor.main import MIDIQueueVizor                        # How we are sending messages to a MIDI device
import mido                                                             # MIDI I/O Framework
import threading                                                        # For managing the event loop of those queues
import signal                                                           # For shutting down vizor when server is stopped
from midi_queue_message.MIDINoteMessageOn import MIDINoteMessageOn      # For sending NOTE_ON MIDI messages
from midi_queue_message.MIDINoteMessageOff import MIDINoteMessageOff    # For sending NOTE_OFF MIDI messages   
from midi_queue_message.MIDIMessageChord import MIDIMessageChord        # For sending the MIDI Messages of a chord
from midi_queue_message.MIDIMessageStop import MIDIMessageStop          # For stopping all the active notes of a specific channel
from midi_queue_message.MIDIMessageControl import MIDIMessageControl    # For sending CONTROL_CHANGE MIDI messages
from midi_queue_message.MIDIMessageNotes import MIDIMessageNotes        # For sending multiple MIDI NOTE ON messages
from midi_cast_xml.main import MIDICastXML                              # For processing MIDI messages using XML
from flask_cors import CORS                                             # For setting CORS

class MIDICastServer:

    """Implements an HTTP server for relaying requests to a MIDI device"""

    ###############
    # CONSTRUCTOR #
    ###############
    
    def __init__(self, outport : mido.ports.BaseOutput):
        self.vizor =  MIDIQueueVizor.initChannels(outport) # Initializes process for managing messages to a MIDI device
        self.app = Flask(__name__)                         # Create an instance of the Flask app as a property of the class
        
        # TODO: Dont accept CORS from EVERYONE:
        CORS(self.app)
        
        
        self.initRoutes()                                  # Initalizes routes for Flask server 

    ####################
    # Instance Methods #
    ####################

    def initRoutes(self):
        """Initalizes routes for Flask server"""
        
        # GET :: / 
        @self.app.route('/', methods=["GET"])
        def get_index():
            return "Yo. Things are Running. Probably. LOLLERZ!!!!1111"
        
        # POST :: /on/:channel
        @self.app.route("/on/<channel>", methods=["POST"])
        def create_note_on(channel):
            """Creates a NOTE_ON MIDI message"""
            try:

                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                note = body.get("note")
                gate = MIDICastServer.setGate(body)
                velocity = MIDICastServer.setVelocity(body)

                # Create NOTE_ON message to send to the channel of a device:
                msg = MIDINoteMessageOn(channel=channel, note=note, gate=gate, velocity=velocity)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200
        
            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500
            
        # POST :: /on/:channel
        @self.app.route("/off/<channel>", methods=["POST"])
        def create_note_off(channel):
            """Creates a NOTE_OFF MIDI message"""
            try:

                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                note = body.get("note")
                gate = MIDICastServer.setGate(body)
                velocity = MIDICastServer.setVelocity(body)

                # Create NOTE_ON message to send to the channel of a device:
                msg = MIDINoteMessageOff(channel=channel, note=note, gate=gate, velocity=velocity)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200
        
            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500

        # POST :: /notes/:channel
        @self.app.route("/notes/<channel>", methods=["POST"])
        def send_notes(channel):
            """Send multiple notes for the given channel"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()

                notes = body.get("notes")
                gate = MIDICastServer.setGate(body)
                velocity = MIDICastServer.setVelocity(body)

                # Send to the channel of a device:
                msg = MIDIMessageNotes(channel=channel, notes=notes, gate=gate, velocity=velocity)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500

        # POST :: /chord/:channel
        @self.app.route("/chord/<channel>", methods=["POST"])
        def send_chord(channel):    
            """Send multiple MIDI messages for playing a chord"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                tonic = body.get("note")
                degrees = body.get("degrees")
                scale = body.get("scale")
                transpose = body.get("transpose")
                gate = MIDICastServer.setGate(body)
                velocity = MIDICastServer.setVelocity(body)

                # Create messages to send to the channel of a device:
                msg = MIDIMessageChord(channel, tonic, degrees, scale, transpose, gate, velocity)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500
            
        # POST :: /cc/:channel
        @self.app.route("/cc/<channel>", methods=["POST"])
        def create_cc_message(channel):
            """Sends a CONTROL_CHANGE MIDI message for the given channel"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                cc = int(body.get("cc"))
                value = body.get("value")
                gate = MIDICastServer.setGate(body)
        
                # Create CHANGE_CONTROL message to send to the channel of a device:
                msg = MIDIMessageControl(channel, cc, value, gate)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500
            
        # POST :: /cc/:channel/on
        @self.app.route("/cc/<channel>/on", methods=["POST"])
        def cc_message_on(channel):
            """Sends a CONTROL_CHANGE MIDI message toggling ON a parameter"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                cc = int(body.get("cc"))
                gate = MIDICastServer.setGate(body)
        
                # Create CHANGE_CONTROL message to send to the channel of a device:
                msg = MIDIMessageControl(channel, cc, 127, gate)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500
            
        # POST :: /cc/:channel/off
        @self.app.route("/cc/<channel>/off", methods=["POST"])
        def cc_message_off(channel):
            """Sends a CONTROL_CHANGE MIDI message toggling OFF a parameter"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                cc = int(body.get("cc"))
                gate = MIDICastServer.setGate(body)
        
                # Create CHANGE_CONTROL message to send to the channel of a device:
                msg = MIDIMessageControl(channel, cc, 0, gate)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500
            
        # POST :: /cc/:channel/sweep
        @self.app.route("/cc/<channel>/sweep", methods=["POST"])
        def sweep_cc(channel):
            """Sends a series of CONTROL_CHANGE MIDI message for the given channel"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                cc = int(body.get("cc"))
                x1, y1, x2, y2 = body.get("value")  # This intended to be an array of values for a bezier curve
                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)
                start = body.get("start")
                stop = body.get("stop")
                steps =  body.get("steps")
                gate = MIDICastServer.setGate(body)
        
                # Create CHANGE_CONTROL messages to send to the channel of a device:
                values = MIDIMessageControl.cubic_bezier_midi_cc(x1, y1, x2, y2, start, stop, steps)
                msgs = MIDIMessageControl.cc_sweep(channel=channel, cc=cc, values=values, gate=gate)

                # Relay message to intended channel:
                for msg in msgs:
                    self.vizor.relay(msg)

                # Send relayed message as response to request:
                return ("True", 200)

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500
            
        # POST :: /cc/:channel/sweep/:easing
        @self.app.route("/cc/<channel>/sweep/<easing>", methods=["POST"])
        def cc_easeing(channel, easing):
            """Applies specific easing function to a series of CC values for a given CC parameters of a given channel"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                cc = int(body.get("cc"))
                start = int(body.get("start"))
                stop = int(body.get("stop"))
                steps =  int(body.get("steps"))
                gate = MIDICastServer.setGate(body)
        
                # Create CHANGE_CONTROL messages to send to the channel of a device:
                if easing == "ease-in":
                    msgs = MIDIMessageControl.easeIn(channel, cc, start, stop, gate, steps)
                elif easing == "ease-out":
                    msgs = MIDIMessageControl.easeOut(channel, cc, start, stop, gate, steps)
                elif easing == "linear":
                    msgs = MIDIMessageControl.linear(channel, cc, start, stop, gate, steps)
                else:
                    raise ValueError(f"Unsupported easing function: {easing}")

                # Relay message to intended channel:
                for msg in msgs:
                    self.vizor.relay(msg)

                # Send relayed message as response to request:
                return ("True", 200)

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500

        # POST :: /stop/:channel
        @self.app.route("/stop/<channel>", methods=["POST"])
        def create_channel_stop(channel):
            """Stops all active notes for the given channel"""
            try:
            
                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Get the JSON data from the request body
                body = request.get_json()
                gate = MIDICastServer.setGate(body)

                 # Create NOTE_ON message to send to the channel of a device:
                msg = MIDIMessageStop(channel=channel, gate=gate)

                # Relay message to intended channel:
                self.vizor.relay(msg)

                # Send relayed message as response to request:
                return str(msg), 200

            except Exception as e:
                
                print(e)
                return jsonify({"error":str(e)}), 500
            
        # GET :: /clear/:channel
        @self.app.route("/clear/<channel>", methods=["GET"])
        def clear_channel(channel):   
            "Stops all active notes and clears all messages for a given channel"
            try:

                # Get channel from dynamic URL segment
                channel = MIDICastServer.setChannel(channel)

                # Clear channel:
                self.vizor.clear(channel)

                # Send sucess response:
                return ("True", 200)

            except Exception as e:

                print(e)
                return jsonify({"error":str(e)}), 500
            
        # GET :: /panic
        @self.app.route("/panic", methods=["GET"])
        def panic():   
            "Stops all active notes and clears all messages for all  channels"
            try:

                # Clear channel:
                self.vizor.panic()

                # Send sucess response:
                return ("True", 200)

            except Exception as e:

                print(e)
                return jsonify({"error":str(e)}), 500
            
        # POST :: /xml
        @self.app.route("/xml", methods=["POST"])
        def play_xml():   
            "Plays the given XML"
            try:

                # Ensure that the request's content type is XML
                if request.content_type != 'application/xml':
                    return Response("Invalid content type", status=400)

                # Read the raw XML data from the request body, transform XML into message, and then send to viozr:
                MIDICastXML.init(request.data, self.vizor)

                # Send sucess response:
                return jsonify({"success":True}), 200

            except Exception as e:

                print(e)
                return jsonify({"error":str(e)}), 500
            
    def stopVizor(self, signum=None, frame=None):
        """Handles shutting down vizor using signal since Flask is already handling shutdown"""
        self.vizor.stop()
        sys.exit(0)  # Gracefully exit the application

    def start(self, host="127.0.0.1", port=5000) -> threading.Thread:
        """Starts vizor and server"""
        # Set up signal handlers to catch SIGINT (CTRL+C) and SIGTERM
        signal.signal(signal.SIGINT, self.stopVizor)  # CTRL+C (SIGINT)
        signal.signal(signal.SIGTERM, self.stopVizor)  # SIGTERM (for other shutdown scenarios)
        self.vizor.start()                              # Start queues for handling MIDI messages from requests    
        self.app.run(host=host, port=port, debug=True)  # Start Server

    ##################
    # Static Methods #
    ##################

    @staticmethod
    def setChannel(value) -> int:
        return int(value) - 1

    @staticmethod
    def setGate(body : typing.Dict) -> int:
        """Ensure "gate" value from request is valid"""
        gate = body.get("gate")
        if gate == "None" or gate == "null" or gate is None:
            return gate 
        else:
            num = float(gate)
            # Check if it's an integer in float form
            if num.is_integer():
                return int(num)
            return num 

    @staticmethod
    def setVelocity(body : typing.Dict) -> int:
        """Ensure "velocity" value from request is valid"""
        velocity = body.get("velocity")
        None if velocity == "None" or velocity == "null" or velocity is None else int(velocity)

# Example usage
if __name__ == "__main__":

    # TODO: Probably need better way of selecting ports:
    outport = mido.open_output("E-MU XMidi1X1 Tab:E-MU XMidi1X1 Tab Out 20:0") 

    # Initalize server:
    server = MIDICastServer(outport)

    # Start Server
    server.start(port=5001)
    
