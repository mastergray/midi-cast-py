# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from midi_queue_message.MIDIMessageControl import MIDIMessageControl

class MIDICastXMLRest:

    '''Transforms CONTROL element into a MIDIMessageControl message'''

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, elem):
        if elem.tag == "note":
            self.channel = elem.attrib.get("channel")
            self.cc = elem.attrib.get("cc")
            self.value = elem.attrib.get("value")
            self.gate = elem.attrib.get("gate", None)
        else:
            raise ValueError(f"Expected REST tag but recieved '{elem.tag}' instead")

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
    def gate(self):
        return self._gate
    
    @gate.setter
    def gate(self, value) -> None:
        try:
            self._gate = int(value)
        except ValueError:
            try:
                self._gate = float(value)
            except ValueError:
                raise ValueError(f"Cannot set '{value}' as gate")

    @property
    def cc(self):
        return self._channel
    
    @cc.setter
    def cc(self, value) -> None:
        self._cc = int(value)

    @property
    def value(self):
        return self._value
    
    @cc.setter
    def value(self, value) -> None:
        self._value = int(value)

    #################
    # Magic Methods #
    #################

    def __call__(self, messages) -> None:
        """Transforms stored element into a message that's added to the given array"""
        message = MIDIMessageControl(
            channel=self.channel, 
            cc=self.cc, 
            value=self.value,
            gate=self.gate, 
        )
        messages.append(message)

    # Static Methods #

    @staticmethod
    def init(elem, messages):
        """A static factory method for initalizing an instance and storing transform to a result"""
        message = MIDIMessageControl(elem)
        message(messages)
