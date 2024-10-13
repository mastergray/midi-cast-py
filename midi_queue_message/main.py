from __future__ import annotations  # Allows forward references in type hints
import typing
if typing.TYPE_CHECKING:
    from midi_queue.main import MIDIQueue   # For annotating MIDIQueue type in "call" magic method

# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
import json                             # For representing instance as JSON
from abc import ABC, abstractmethod     # For denoting methods intended to be overwritten by a child class

class MIDIQueueMessage (ABC):
    
    """Base class representing a generic MIDI message to be processed by a MIDIQueue"""

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, channel: int):
        self.channel = channel  # MIDI message data in dictionary format

    ##############
    # Properties #
    ##############

    @property
    def channel(self) -> int:
        """GETTER for MIDI channel intended for this message"""
        return self._channel 
    
    @channel.setter
    def channel(self, channel:int) -> None:
        """SETTER for MIDI channel intended for this message"""
        self._channel = channel

    #################
    # Magic Methods #
    #################

    def __str__(self) -> str:
        """How to represent a MIDIDNoteMessage instance as a STRING"""
        return json.dumps(vars(self))
    
    @abstractmethod
    async def __call__(self, queue : "MIDIQueue" = None) -> None:
        """How this message is processed by the given queue"""
        pass
