# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from typing import Union                                           # For annotating a value that maybe of more than one possible type
import asyncio                                                     # For using async operations (like sleep)
import mido                                                        # For sending MIDI messages
from midi_queue_message.MIDINoteMessage import MIDINoteMessage     # Base class we are extending from
from midi_queue.main import MIDIQueue                              # For annotating MIDIQueue type in "call" magic method

class MIDINoteMessageOn (MIDINoteMessage):

    "Implements a NOTE_ON MIDI message that can be sent to a MIDIQueue for processing"

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, channel : int , note : Union[int,str], gate : Union[int, float, None] = None, velocity: Union[int, None] = None):
        super().__init__(channel=channel, note=note, gate=gate, velocity=velocity)
        # Setting Message type, mainly for debugging purposes:
        self._msgType = "note_on"

    #################
    # Magic Methods #
    #################

    async def __call__(self, queue: "MIDIQueue" = None):

        try:

            """Implements how to process a NOTE_ON MIDI message with optional gate delay"""
            # NOTE: If no queue is set, we print the message when called
            # Initialize and send message if queue is set:
            if queue is not None and queue.active is True:
                queue.addActiveNote(self.noteValue)
                message = mido.Message("note_on", channel=self.channel, note=self.noteValue, velocity=self.velocity)
                queue.vizor.send(message)
            else:
                print(self)

            # Play message for a specific amount of time, otherwise note play until a note_off message is sent:
            if self.gate is not None:
                await asyncio.sleep(self.gate) 
                # Send NOTE_OFF message is there is a queue set for this message:
                if queue is not None and queue.active is True:
                    queue.removeActiveNote(self.noteValue)
                    message = mido.Message("note_off", channel=self.channel, note=self.noteValue, velocity=self.velocity)
                    queue.vizor.send(message)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Example usage
if __name__ == "__main__":

    # Print messages by "calling them":
    async def main(notes):
        for note in notes:
            await note()

    # Create some message:
    notes = [
        MIDINoteMessageOn(channel=0, note="C4", gate=1),
        MIDINoteMessageOn(channel=1, note=75, gate=2),
        MIDINoteMessageOn(channel=2, note="A#2", gate=.25),
        MIDINoteMessageOn(channel=3, note=69, gate=1, velocity=64)
    ]

    # Call notes:
    asyncio.run(main(notes))


    