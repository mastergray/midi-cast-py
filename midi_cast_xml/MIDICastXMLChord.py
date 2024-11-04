# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from midi_queue_message.MIDIMessageChord import MIDIMessageChord

class MIDICastXMLChord:

    '''Transforms CHORD element into a MIDIMessageChord message'''

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, elem):
        if elem.tag == "chord":
            self.channel = elem.attrib.get("channel")
            self.gate = elem.attrib.get("gate", None)
            self.velocity = elem.attrib.get("velocity", None) 
            self.degrees = elem.attrib.get("tones")
            self.tonic = elem.attrib.get("tonic")
            self.transpose = elem.attrib.get("transpose", None)
            self.scale = elem.attrib.get("scale", None)
        else:
            raise ValueError(f"Expected CHORD tag but recieved '{elem.tag}' instead")

    ##############
    # Properties #
    ##############

    #---------#
    # channel #
    #---------#

    @property
    def channel(self):
        return self._channel
    
    @channel.setter
    def channel(self, value) -> None:
        self._channel = int(value) - 1

    #------#
    # gate #
    #------#

    @property
    def gate(self):
        return self._gate
    
    @gate.setter
    def gate(self, value) -> None:
        try:
            if value is None:
                self._gate = value 
            else:
                self._gate = int(value)
        except ValueError:
            try:
                self._gate = float(value)
            except ValueError:
                raise ValueError(f"Cannot set '{value}' as gate")

    #----------#
    # velocity #
    #----------#

    @property
    def velocity(self):
        return self._velocity
    
    @velocity.setter
    def velocity(self, value) -> None:
        self._velocity = None if value is None else int(value)

    #---------#
    # degrees #
    #---------#

    @property
    def degrees(self):
        return self._degrees
    
    @degrees.setter
    def degrees(self, value) -> None:
        self._degrees = value.split(",") 

    #-------#
    # tonic #
    #-------#

    @property
    def tonic(self):
        return self._tonic
    
    @tonic.setter
    def tonic(self, value) -> None:
        self._tonic = value

    #-----------#
    # transpose #
    #-----------#

    @property
    def transpose(self):
        return self._transpose
    
    @transpose.setter
    def transpose(self, value) -> None:
        self._transpose = value

    #-------#
    # scale #
    #-------#

    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value) -> None:
        self._scale = None if value is None else [int(num) for num in value.split('-')]
   
    #################
    # Magic Methods #
    #################

    def __call__(self, messages) -> None:
        """Transforms stored element into a message that's added to the given array"""
        message = MIDIMessageChord(
            channel=self.channel, 
            tonic=self.tonic,
            degrees=self.degrees, 
            transpose=self.transpose,
            scale=self.scale,
            gate=self.gate,
            velocity=self.velocity
        )
        messages.append(message)

    # Static Methods #

    @staticmethod
    def init(elem, messages):
        """A static factory method for initalizing an instance and storing transform to a result"""
        message = MIDICastXMLChord(elem)
        message(messages)
