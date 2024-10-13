# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from typing import Union, List                                     # For annotating a value that maybe of more than one possible type
import asyncio                                                     # For using async operations (like sleep)
import mido                                                        # For sending MIDI messages
from midi_queue_message.main import MIDIQueueMessage               # Base class we are extending from
from midi_queue_message.MIDINoteMessage import MIDINoteMessage     # Using static methods for note value lookup
from midi_queue.main import MIDIQueue                              # For annotating MIDIQueue type in "call" magic method
import json                                                        # Used for returning MIDIMessageChord as a STRING

class MIDIMessageChord (MIDIQueueMessage):

    "Implements a MIDI message for playing a chord of notes that can be sent to a MIDIQueue for processing"

    # Static field for some predefined scale patterns:
    SCALES = {
         "Major":[2, 2, 1, 2, 2, 2, 1, 2, 2, 1, 2, 2],
         "Minor":[2, 1, 2, 2, 1, 2, 2, 2, 1, 2, 2, 1]
    }

    # Static field for some predefined chord formulas:
    CHRORDS = {
        "maj":["1", "3", "5"], 
        "min":["1", "3b", "5"], 
        "dom7":["1", "3", "5", "7b"],
        "maj7":["1", "3", "5", "7"],
        "min7":["1", "3b", "5", "7b"],
        "dim":["1", "3b", "5b"],
        "dim7":["1", "3b", "5b", "7d"]
    }

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, channel : int , tonic : Union[int,str], degrees : List[str], scale : Union[List[int], None] = None, transpose : str = None, gate : Union[int, float, None] = None, velocity: int = 127):
        super().__init__(channel=channel)
        self.tonic = tonic          # "Tonic" of scale chord is built from
        self.scale = scale          # Defines distance of notes from tonic to build chord from 
        self.root = transpose       # Determins root of chord (we use the "tonic" as the root if there is nothing to transpose)
        self.tones = degrees        # Defines notes of chord using scale steps and the root
        self.gate = gate            # Determines long to play chord (in seconds)
        self.velocity = velocity    # Determines how loud to play chord 
        self._msgType = "chord"     # For debugging purposes

    ##############
    # Properties #
    ##############

    @property
    def tonic(self) -> int:
        """GETTER for "tonic" of scale and chord"""
        return self._tonic 
    
    @tonic.setter
    def tonic(self, value : Union[int,str]) -> None:
        """SETTER for "tonic" of scale and chord"""
        if isinstance(value, str):
            self._tonic = MIDINoteMessage.lookup(value)
        elif isinstance(value, int):
            if value >= 21 and value <= 108:
                self._note = value 
            else:
                raise ValueError(f"MIDI Note Value '{value}' Not In Range: 21 >= INT <= 108") 
        else:
            raise TypeError("Can Only Set Tonic Using Either A STRING Or INTEGER")
         
    @property
    def scale(self) -> int:
        """GETTER for scale used to build chord from"""
        return self._scale 
    
    @scale.setter
    def scale(self, value : Union[List[int], None]) -> None:
        """GETTER for scale used to build chord from"""
        scale = MIDIMessageChord.SCALES.get("Major") if value is None else value
        step = 0
        self._scale = [step]
        for distance in scale:
            step += distance 
            self._scale.append(step)  

    @property
    def tones(self) -> List[int]:
        """GETTER for notes of chord"""
        return self._tones 
    
    @tones.setter
    def tones(self, value : List[str]) -> None:
        """SETTER for notes of chord"""
        self._tones = [MIDIMessageChord.degree(degree, self.scale, self.root) for degree in value]

    @property
    def root(self) -> List[int]:
        """GETTER for root of chord"""
        return self._root
    
    @root.setter
    def root(self, value : str) -> None:
        """SETTER for root of chord"""
        self._root = MIDIMessageChord.degree(value, self.scale, self.tonic) if value is not None else self.tonic 

    #################
    # Magic Methods #
    #################

    # TODO: Clean up instance fields so they work similar to MIDINoteMessage for a more consistent interface
    def __str__(self):
        """"Returns MIDINoteMessageChord as a list of note names"""
        # Get A copy of the properties of chord:
        chord = vars(self).copy()
        # Properties to add:
        chord["_noteValue"] = self._tones 
        chord["_noteName"] =  ", ".join([MIDINoteMessage.reverseLookup(tone) for tone in self._tones])
        chord["_gate"] = self.gate 
        chord["_velocity"] = self.velocity
        # Properties to remove:
        del chord["_tones"]
        del chord["gate"]
        del chord["velocity"]
        del chord["_scale"]
        # Transform dictionary into string:
        return json.dumps(chord)
    

    async def __call__(self, queue : "MIDIQueue" = None) -> None:
        """How this message is processed by the given queue"""
        try:

            """Implements how to process a NOTE_ON MIDI message with optional gate delay"""
            # NOTE: If no queue is set, we print the message when called
            # Initialize and send message if queue is set:
            if queue is not None and queue.active is True:
                for tone in self.tones:
                    queue.addActiveNote(tone)
                    message = mido.Message("note_on", channel=self.channel, note=tone, velocity=self.velocity)
                    queue.vizor.send(message)
            else:
                print(self)

            # Play chord tones for a specific amount of time, otherwise note play until a note_off messages for all tones is sent:
            if self.gate is not None:
                await asyncio.sleep(self.gate) 
                # Send NOTE_OFF messages if there is a queue set for this message:
                if queue is not None and queue.active is True:
                    for tone in self.tones:
                        queue.removeActiveNote(tone)
                        message = mido.Message("note_off", channel=self.channel, note=tone, velocity=self.velocity)
                        queue.vizor.send(message)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    ##################
    # Static Methods #
    ##################

    @staticmethod
    def degree(degree : str, scale : List[int], tonic : int):
        """Returns MIDI note number for given degree of scale"""
        # A "negative" degree is prepended with a negative sign, e.g. "-5b" would be a flatten Fifth below the root:
        isNegative = degree[0] == "-"
         # Flat
        if degree[-1] == "b":
            scaleDistanceIndex = int(degree[:-1]) - 1
            distance = scale[scaleDistanceIndex] - 1     
        # "D"ouble flat:
        elif degree[-1] == "d":
            scaleDistanceIndex = int(degree[:-1]) - 1
            distance = scale[scaleDistanceIndex] - 2
        # Sharp
        elif degree[-1] == "#":
            scaleDistanceIndex = int(degree[:-1]) - 1
            distance = scale[scaleDistanceIndex] + 1
        # "Double "S"harp:
        elif degree[-1] == "s":
            scaleDistanceIndex = int(degree[:-1]) - 1
            distance = scale[scaleDistanceIndex] + 2
        # Natural
        else:
            scaleDistanceIndex = abs(int(degree)) - 1
            distance = scale[scaleDistanceIndex] 
        return tonic - distance if isNegative else distance + tonic 

# Example usage
if __name__ == "__main__":

    '''
    # Print the C Major Scale starting at "middle" C:
    chord = MIDIMessageChord(0, "C4", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"])
    print(chord)
    
    # Print the C Major Scale "below" the tonic:
    chord = MIDIMessageChord(0, "C4", ["-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8", "-9", "-10", "-11", "-12", "-13"])
    print(chord)

    # Print A C Dominant 7th chord
    dom7 = MIDIMessageChord(0, "C4", ["1", "3", "5", "7b"])
    print(dom7)

    # Print a D Minor chord:
    min =  MIDIMessageChord(0, "D4", MIDIMessageChord.CHRORDS.get("min"))
    print(min)

    # Print a F# Diminished 7th chord
    dim7 =  MIDIMessageChord(0, "F#4", ["1", "3b", "5b", "7d"])
    print(dim7)
    '''

    # A simple I - VI - V chord progression in C:
    print(MIDIMessageChord(0, "C4", ["1", "3", "5"], transpose="1"))
    print(MIDIMessageChord(0, "C4", ["1", "3b", "5"], transpose="6"))
    print(MIDIMessageChord(0, "C4", ["1", "3", "5#"], transpose="7b"))




    