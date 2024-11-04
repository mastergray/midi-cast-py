from __future__ import annotations  # Allows forward references in type hints
import typing
if typing.TYPE_CHECKING:
    from midi_queue_vizor.main import MIDIQueueVizor  # Only imported during type checking
   
# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from midi_queue.PrioQueue import PrioQueue             # For managing queues with
import mido                                            # MIDI I/O Framework
import asyncio                                         # Async operations
from midi_queue_message.main import MIDIQueueMessage   # For annotating methods that accept a MIDIQueueMessage

class MIDIQueue:

    """Asynchronous queue for managing MIDI messages intended for a specific MIDI channel"""

    ###############
    # CONSTRUCTOR #
    ###############
    
    def __init__(self, channel, vizor : MIDIQueueVizor):
        self.channel = channel          # MIDI channel for sending messages to
        self.vizor = vizor              # Vizor which manages this queue
        self.queue = PrioQueue()        # Stores messages intended for that channel
        self.activeNotes = {}           # Stores notes which are currently "on"
        self.active = True              # Determines if queue is "active" or not - that is if messages can be recieved or processed

    ##############
    # Properties #
    ##############

    @property
    def active(self) -> bool:
        """GETTER for "active" status of queue and vizor"""
        return self._active and self.vizor.active 
    
    @active.setter
    def active(self, active:bool) -> None:
        """SETTER for "active" status of queue"""
        self._active = active

    ####################
    # Instance Methods #
    ####################

    def add(self, msg : MIDIQueueMessage, hasPrio : bool = False):
        """Add message to queue for processing"""
        # Check to ensure we are trying to send a message using a MIDIQueueMessage object:
        if not isinstance(msg, MIDIQueueMessage):
            raise ValueError(f"Could not add message to channel `${self.channel}` queue: {type(message).__name__}. Expected MIDIQueueMessage")
        if self.active is True:
            coroutine = self.queue.put_front(msg) if hasPrio is True else self.queue.put(msg)
            return asyncio.run_coroutine_threadsafe(coroutine, self.vizor.eventLoop)
        else:
            print(f"Message for channel queue '{self.channel}' not added since queue is not active")
    
    async def consumer(self):
        """Coroutine used by the event loop to process the next message in queue"""
        while True:
            msg = await self.queue.get()   # Wait for an item from the queue
            try:
                if self.active is True:
                    print(msg)
                    await msg(self)        # MIDIQueueMessage uses "callable" magic method for being processed
                else:
                    print(f"Message for channel queue '{self.channel}' not processed since queue is not active")
            except asyncio.CancelledError:
                # Keeping this here in case we need to handle anything else when shutting down the event loop
                # self.clear()
                pass
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            finally:
                self.queue.task_done()     # Mark the task as done
 
    def addActiveNote(self, noteValue : int):
        """Add an active note to the 'activeNotes' cache by noteValue"""
        if noteValue not in self.activeNotes:
            self.activeNotes[noteValue] = True

    def removeActiveNote(self, noteValue : int):
        """Remove an active note from the 'activeNotes' cache by noteValue"""
        if noteValue in self.activeNotes:
            del self.activeNotes[noteValue]

    def stop(self):
        """Stops all active notes in queue"""
        # Send note_off messages for all active notes:
        for noteValue, note in self.activeNotes.items():
            message = mido.Message("note_off", channel=self.channel, note=noteValue, velocity=0)
            self.vizor.outport.send(message)       # Reset active notes:
        self.activeNotes = {}

    def clear(self):
        """Stops all notes and clears all messages from queue"""
        # Deactive queue so no new messages are recieved:
        self.active = False 
        # Send note_off messages for all active notes:
        self.stop()
        # Reset queue:
        self.queue.clear()
        # Re-enable queue:
        self.active = True 

# Example usage
if __name__ == "__main__":
    
    try:
        
        # Import MIDI notes to send:
        from midi_queue_message.MIDINoteMessageOn import MIDINoteMessageOn   
        from midi_queue_message.MIDINoteMessageOff import MIDINoteMessageOff    
        from midi_queue_vizor.main import MIDIQueueVizor  

        # Initialize queue using vizor
        vizor = MIDIQueueVizor.initChannels(0,3)
        
        # Create some notes to send:
        notes = [
            MIDINoteMessageOn(channel=0, note="C4", gate=1),
            MIDINoteMessageOn(channel=1, note=75, gate=2),
            MIDINoteMessageOn(channel=2, note="A#2", gate=.25),
            MIDINoteMessageOn(channel=3, note=69, gate=1, velocity=64),
            MIDINoteMessageOff(channel=0, note="C4", gate=1),
            MIDINoteMessageOff(channel=1, note=75, gate=2),
            MIDINoteMessageOff(channel=2, note="A#2", gate=.25),
            MIDINoteMessageOff(channel=3, note=69, gate=1, velocity=64)
        ]
        
        # Start Queue
        eventLoopThread = vizor.start()
        
        # Send notes to queue
        for note in notes:
            vizor.relay(note)
        
        # Keep the main program running to let queues process messages
        # Since the thread is a daemon, we need to manually manage the time we keep the script running
        while eventLoopThread.is_alive():
            eventLoopThread.join(timeout=1)
    
    except KeyboardInterrupt:
    
        # Shutdown vizor on keyboard 
        vizor.stop()



