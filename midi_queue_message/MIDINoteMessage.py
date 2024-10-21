# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from typing import Union                               # For annotating a value that maybe of more than one possible type
from midi_queue_message.main import MIDIQueueMessage   # Base class we are extending from
from midi_queue.main import MIDIQueue                  # For annotating MIDIQueue type in "call" magic method

class MIDINoteMessage(MIDIQueueMessage):

    """Base class representing a generic MIDI message to be processed by MIDIQueue"""

    # Maps Note Name to MIDI Number for an 88 key piano:
    NoteNameToMIDINumber = {
        "A0":21,
        "A#0":22,
        "B0":23,
        "C1":24,
        "C#1":25,
        "D1":26,
        "D#1":27,
        "E1":28,
        "F1":29,
        "F#1":30,
        "G1":31,
        "G#1":32,
        "A1":33,
        "A#1":34,
        "B1":35,
        "C2":36,
        "C#2":37,
        "D2":38,
        "D#2":39,
        "E2":40,
        "F2":41,
        "F#2":42,
        "G2":43,
        "G#2":44,
        "A2":45,
        "A#2":46,
        "B2":47,
        "C3":48,
        "C#3":49,
        "D3":50,
        "D#3":51,
        "E3":52,
        "F3":53,
        "F#3":54,
        "G3":55,
        "G#3":56,
        "A3":57,
        "A#3":58,
        "B3":59,
        "C4":60, # Middle C
        "C#4":61,
        "D4":62,
        "D#4":63,
        "E4":64,
        "F4":65,
        "F#4":66,
        "G4":67,
        "G#4":68,
        "A4":69, # Nice
        "A#4":70,
        "B4":71,
        "C5":72,
        "C#5":73,
        "D5":74,
        "D#5":75,
        "E5":76,
        "F5":77,
        "F#5":78,
        "G5":79,
        "G#5":80,
        "A5":81,
        "A#5":82,
        "B5":83,
        "C6":84,
        "C#6":85,
        "D6":86,
        "D#6":87,
        "E6":88,
        "F6":89,
        "F#6":90,
        "G6":91,
        "G#6":92,
        "A6":93,
        "A#6":94,
        "B6":95,
        "C7":96,
        "C#7":97,
        "D7":98,
        "D#7":99,
        "E7":100,
        "F7":101,
        "F#7":102,
        "G7":103,
        "G#7":104,
        "A7":105,
        "A#7":106,
        "B7":107,
        "C8":108
    }

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, channel : int , note : Union[int,str], gate : Union[int, float, None] = None, velocity: Union[int, None] = None):
        super().__init__(channel=channel)
        self.noteValue = note       # MIDI Note value of message
        self.noteName = note        # Name of musical note represented by the MIDI not value
        self.gate = gate            # How long to play the note for 
        self.velocity = velocity    # How loud the note should be

    ##############
    # Properties #
    ##############

    @property
    def noteValue(self) -> int:
        """GETTER for MIDI "note" value to for this message"""
        return self._noteValue 
    
    @noteValue.setter
    def noteValue(self, value: Union[str, int]) -> None:  
        """GETTER for MIDI "note" value to for this message"""
        if isinstance(value, str):
            self._noteValue = MIDINoteMessage.lookup(value)
        elif isinstance(value, int):
            if value >= 21 and value <= 108:
                self._noteValue = value 
            else:
                raise ValueError(f"MIDI Note Value '{value}' Not In Range: 21 >= INT <= 108") 
        else:
            raise TypeError("Can Only Set Note Value Using Either A STRING Or INTEGER")
        
    @property
    def noteName(self) -> str:
        """GETTER for MIDI "note" name of this message"""
        return self._noteName 
    
    @noteName.setter
    def noteName(self, value:Union[int, str]) -> None:       
        """SETTER for MIDI "note" name of this message"""
        if isinstance(value, str):
            self._noteName = value
        elif isinstance(value, int):
            self._noteName = MIDINoteMessage.reverseLookup(value)
        else:
            raise TypeError("Can Only Set Note Name Using Either A STRING Or INTEGER")
        
    @property
    def gate(self) -> int:
        """GETTER for how long message should be processed for"""
        return self._gate 
    
    @gate.setter
    def gate(self, value:Union[None, int, float] = None) -> None:
        """SETTER for how long message should be processed for"""
        if isinstance(value, int) or isinstance(value, float) or value is None:
            self._gate = value 
        else:
            print(value)
            raise TypeError("Can Only Set Message Gate Value Using NONE, FLOAT or an INTEGER")
        
    @property
    def velocity(self) -> int:
        """GETTER for how "loud" message should be processed for"""
        return self._velocity 
    
    @velocity.setter
    def velocity(self, value:Union[None, int] = None) -> None:
        """SETTER for how "loud" message should be processed for"""
        if isinstance(value, int):
            if value >= 0 and value <= 127:
                self._velocity = value 
            else:
                raise ValueError(f"MIDI Velocity Value '{value}' Not In Range: 0 >= INT <= 127") 
        elif value is None:
            self._velocity = 127
        else:
            raise TypeError("Can Only Set MIDI Velocity Value Using Either NONE or an INTEGER")

 
    #################
    # Magic Methods #
    #################

    async def __call__(self, queue : "MIDIQueue" = None) -> None:
        """How this message is processed by the given queue"""
        print(self)

    ##################
    # Static Methods #
    ##################

    @classmethod
    def lookup(cls, value : str) -> int:
        """Returns MIDI note value for the given note name"""
        if isinstance(value, str):
            try:
                return cls.NoteNameToMIDINumber[value]
            except KeyError:
                raise ValueError(f"Invalid Note Name '{value}' Given")
            except:
                pass
        else:
            raise TypeError("Can Only Lookup Note Value Using A STRING")
        
    # MIDINote.lookup :: INTEGER -> STRING
    @classmethod
    def reverseLookup(cls, value : int) -> str:
        """Returns note name for given MIDI note value"""
        if isinstance(value, int):
            if value >= 21 and value <= 108:
                for key, noteValue in cls.NoteNameToMIDINumber.items():
                    if noteValue == value:
                        return key
            else:
                raise ValueError(f"MIDI Note Value '{value}' Not In Range: 21 >= INT <= 108")
        else:
             raise TypeError("Can Only Reverse Lookup Note Name Using An INTEGER")
        
# Example usage
if __name__ == "__main__":

    import asyncio # We need to import this so we can call the async "call" magic method of an initialized MIDINoteMessage

    # Print messages by "calling them":
    async def main(notes):
        for note in notes:
            await note();

    # Create some message:
    notes = [
        MIDINoteMessage(channel=0, note="C4"),
        MIDINoteMessage(channel=1, note=75),
        MIDINoteMessage(channel=2, note="A#2", gate=.25),
        MIDINoteMessage(channel=3, note=69, gate=1, velocity=64)
    ]

    # Call notes:
    asyncio.run(main(notes))

