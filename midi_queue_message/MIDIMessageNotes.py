# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from typing import Union, List                                  # For annotating a value that maybe of more than one possible type
import asyncio                                                  # For using async operations (like sleep)
import mido                                                     # For sending MIDI messages
from midi_queue_message.main import MIDIQueueMessage            # Base class we are extending from
from midi_queue.main import MIDIQueue                           # For annotating MIDIQueue type in "call" magic method
from midi_queue_message.MIDINoteMessage import MIDINoteMessage  # For initializing "notes" with
from midi_queue_message.MIDIMessageStop import MIDIMessageStop  # For supporting "rests" in provided "note" values:


class MIDIMessageNotes (MIDIQueueMessage):

    "Implements multiple NOTE_ON MIDI messages that can be sent to a MIDIQueue for processing"

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, channel : int , notes : Union[int,str], gate : Union[int, float, None] = None, velocity: Union[int, None] = None):
        super().__init__(channel=channel)
        self.noteValues = notes
        self.noteNames = notes
        self.gate = gate 
        self.velocity = velocity
        self._msgType = "notes" # Setting Message type, mainly for debugging purposes:

    ##############
    # Properties #
    ##############

    @property
    def noteValues(self) -> int:
        """GETTER for MIDI "note" values of this message"""
        return self._noteValues
    
    @noteValues.setter
    def noteValues(self, value: Union[str, int]) -> None: 
        """SETTER for MIDI "note" values of this message"""
        noteValues = []
        for note in value:
            noteValue = MIDINoteMessage(channel=self.channel, note=note).noteValue
            noteValues.append(noteValue)
        self._noteValues = noteValues
        
    @property
    def noteNames(self) -> str:
        """GETTER for MIDI "note" names of this message"""
        return self._noteNames
    
    @noteNames.setter
    def noteNames(self, value:Union[MIDINoteMessage, MIDIMessageStop]) -> None:    
        """SETTER for MIDI "note" names of this message"""
        noteNames = []
        for note in value:
            noteName = MIDINoteMessage(channel=self.channel, note=note).noteName
            noteNames.append(noteName)
        self._noteNames = ", ".join(noteNames)

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
        try:
            """Implements how to process a NOTE_ON MIDI message with optional gate delay"""
            # NOTE: If no queue is set, we print the message when called
            # Initialize and send message if queue is set:
            if queue is not None and queue.active is True:
                for note in self.noteValues:
                    queue.addActiveNote(note)
                    message = mido.Message("note_on", channel=self.channel, note=note, velocity=self.velocity)
                    queue.vizor.send(message)
            else:
                print(self)

            # Play chord tones for a specific amount of time, otherwise note play until a note_off messages for all tones is sent:
            if self.gate is not None:
                await asyncio.sleep(self.gate) 
                # Send NOTE_OFF messages if there is a queue set for this message:
                if queue is not None and queue.active is True:
                    for note in self.noteValues:
                        queue.removeActiveNote(note)
                        message = mido.Message("note_off", channel=self.channel, note=note, velocity=self.velocity)
                        queue.vizor.send(message)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")


# Example usage
if __name__ == "__main__":

    from midi_queue_vizor.main import MIDIQueueVizor  

    try:

        # TODO: Probably need better way of selecting ports:
        outport = mido.open_output("E-MU XMidi1X1 Tab:E-MU XMidi1X1 Tab Out 20:0") 

        # initalize vizor for channels 1-16:
        vizor = MIDIQueueVizor.initChannels(outport)

        # Start queues
        eventLoopThread = vizor.start()

        # Create "notes" message:
        msg = MIDIMessageNotes(channel=0, notes=["C4", "E4", "G4"], gate=1)
    
        # Send Some messages
        vizor.relay(msg)

        # Keep the main program running to let queues process messages
        # Since the thread is a daemon, we need to manually manage the time we keep the script running
        while eventLoopThread.is_alive():
            eventLoopThread.join(timeout=1)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nStopping event loop gracefully...")
        vizor.stop()
        eventLoopThread.join()
        print("Event loop stopped.")


    