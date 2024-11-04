# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from midi_queue_message.MIDIMessageNotes import MIDIMessageNotes

class MIDICastXMLNotes:

    '''Transforms NOTES element into a MIDIMessageNotes message'''

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, elem):
        if elem.tag == "notes":
            self.channel = elem.attrib.get("channel")
            self.notes = elem.attrib.get("tones")
            self.gate = elem.attrib.get("gate", None)
            self.velocity = elem.attrib.get("velocity", None) 
        else:
            raise ValueError(f"Expected NOTES tag but recieved '{elem.tag}' instead")

    ##############
    # Properties #
    ##############

    @property
    def channel(self):
        return self._channel
    
    @channel.setter
    def channel(self, value) -> None:
        self._channel = int(value) - 1

    @property
    def notes(self):
        return self._notes
    
    @notes.setter
    def notes(self, value) -> None:
        self._notes = value.split(",")  

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

    @property
    def velocity(self):
        return self._velocity
    
    @velocity.setter
    def velocity(self, value) -> None:
        self._velocity = None if value is None else int(value)

    #################
    # Magic Methods #
    #################

    def __call__(self, messages) -> None:
        """Transforms stored element into a message that's added to the given array"""
        message = MIDIMessageNotes(channel=self.channel, notes=self.notes, gate=self.gate, velocity=self.velocity)
        messages.append(message)

    # Static Methods #

    @staticmethod
    def init(elem, messages):
        """A static factory method for initalizing an instance and storing transform to a result"""
        message = MIDICastXMLNotes(elem)
        message(messages)
