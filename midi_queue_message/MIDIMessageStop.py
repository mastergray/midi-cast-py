# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from typing import Union, List                                     # For annotating a value that maybe of more than one possible type
import asyncio                                                     # For using async operations (like sleep)
from midi_queue_message.main import MIDIQueueMessage               # Base class we are extending from
from midi_queue.main import MIDIQueue                              # For annotating MIDIQueue type in "call" magic method

class MIDIMessageStop (MIDIQueueMessage):

    """Implements how stop all active MIDI messages of a channel with optional gate delay"""

    def __init__(self, channel : int, gate :Union[int, float, None] = None):
        super().__init__(channel=channel)
        self._gate = gate                   # How long to "rest" for
        self._msgType = "channel_stop"      # Setting Message type, mainly for debugging purposes

    #################
    # Magic Methods #
    #################

    async def __call__(self, queue: "MIDIQueue" = None):
        """Implements how to "stop" all active MIDI messages for a channel with optional gate delay"""
        try:

            # Stop all "active" message of queue if queue is set and active:
            if queue is not None and queue.active is True:
                queue.stop()
            else:
                print(self)

            # How long to wait before next message:
            if self._gate is not None:
                await asyncio.sleep(self._gate) 

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    