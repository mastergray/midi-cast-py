from __future__ import annotations  # Allows forward references in type hints
import typing
if typing.TYPE_CHECKING:
    from midi_queue.main import MIDIQueue                   # Implements queue for sending MIDI messages to

# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
import asyncio                                          # For managing queues with
import threading                                        # For managing the event loop of those queues
import mido                                             # MIDI I/O Framework
from typing import List                                 # For annotating a list of specific types
from midi_queue_message.main import MIDIQueueMessage    # For annotating methods that accept MIDIQueueMessage objects
from midi_queue.main import MIDIQueue                   # Implements queue for sending MIDI messages to

class MIDIQueueVizor:

    """Manages event loop for MIDI message queues"""

    ###############
    # CONSTRUCTOR #
    ###############
    
    def __init__(self, outport : mido.ports.BaseOutput = None):
        self.outport = outport                     # Ouput MIDI device to send messages to
        self.eventLoop = asyncio.new_event_loop()  # The "event loop" being managed
        self.queues = []                           # Stores async queues using that event loop
        self.active = True                         # Determines if vizor should send messages to queues or not

    ####################
    # Instance Methods #
    ####################

    def register(self, channel : int = 0) -> None:
        """Initalizes MIDI queue for a specific channel""" 
        # Initialize a queue using the given MIDI channel and store it in this instance:
        queue = MIDIQueue(channel=channel, vizor=self)
        self.queues.append(queue)
        
    def queue(self, channel: int) -> "MIDIQueue":
        """Returns a stored queue for the given channel, otherwise raises an exception"""
        try:
            return self.queues[channel]
        except IndexError:
            raise IndexError(f"No Queue Found For Channel {channel}")

    def relay(self, message : MIDIQueueMessage):
        """Sends message to queue using channel of message"""
        # Check to ensure we are trying to send a message using a MIDIQueueMessage object:
        if not isinstance(message, MIDIQueueMessage):
            raise ValueError(f"Vizor could not send message to queue: {type(message).__name__}. Expected MIDIQueueMessage")
        # Get queue by channel and send message:
        if self.active is True:
            queue = self.queue(message.channel)
            queue.add(message)
        else:
            print(f"Message to Channel '{message.channel}' not sent since vizor is not currently active")

    def start(self) -> threading.Thread:
        """Initalizes event loop and starts stored queues returning the thread that event loop is running in"""  
        print("Starting MIDI queues....")
        # Reinitialize the event loop if it's been closed
        if self.eventLoop.is_closed():
            self.eventLoop = asyncio.new_event_loop()   
        # Set it as the current event loop:
        if not self.eventLoop.is_running():
            asyncio.set_event_loop(self.eventLoop)
            # Create a consumer task for each queue using their respective `consumer` method
            for queue in self.queues:
                print(f"Starting queue for channel {queue.channel}")
                self.eventLoop.create_task(queue.consumer())     # Add task for queue to event loop
            # Run the event loop in a separate thread
            thread = threading.Thread(target=self.eventLoop.run_forever, daemon=True)
            thread.start()
            print("Vizor Started")
            return thread
        else:
            print("MIDIQueueVizor event loop is already started")
    
    def send(self, msg: mido.Message):
        """Sends MIDI message to MIDI device output if vizor is active:"""
        if not isinstance(msg, mido.Message):
            raise ValueError(f"Vizor could not send message to device: {type(msg).__name__}. Expected mido.Message")
        if isinstance(self.outport,  mido.ports.BaseOutput) and self.active is True:
            self.outport.send(msg)
        else:
            print(msg)

    def stop(self) -> None:
        """Tries to stop the event loop gracefully"""
        # Turn off everything:
        self.panic()
        # Checks if loop is running:
        if self.eventLoop.is_running():
            for task in asyncio.all_tasks(self.eventLoop):
                task.cancel()       # Cancel all running tasks in the event loop  
            self.eventLoop.stop()   # Stop the event loop
            #self.eventLoop.close()  # Close the loop after stopping
        print("Vizor Stopped")

    def clear(self, channel : int):
        """Clears a specific queue by Channel ID"""
        queue = self.queue(channel)
        queue.clear()

    def panic(self) -> None:
        """Immediately stops and clears all queues"""
        # Status message update:
        print("Stopping and reseting all queues...")
        # Deactivate vizor and all queues:
        self.active = False
        # Send "panic" message to MIDI device if device is set:
        if isinstance(self.outport,  mido.ports.BaseOutput):
            self.outport.panic()
        # Manually clear every queues messages and active notes:
        for queue in self.queues:
            queue.queue = asyncio.Queue()    # Initialize new queue to remove existing messages
            queue.activeNotes = {}           # Initialize new active notes cache to remove all existing notes
        # Re-active vizor and queues:
        self.active = True
        # Status message update:
        print("All queues stopped and ready.")


    ##################
    # Static Methods #
    ##################

    @staticmethod
    def initChannels(outport : mido.ports.BaseOutput, fromChannel: int = 0, toChannel: int = 16) -> "MIDIQueueVizor":
        """Initalizes queues to be managed by vizor for some given range of numbers"""
        # NOTE: Channel index starts at 0, not 1 - so Channel 1 would actually be 0
        # Initialize vizor we are creating queues for:
        vizor = MIDIQueueVizor(outport)
        # Register a queue for each channel in range:
        for value in range(fromChannel, toChannel):
            vizor.register(channel=value)
        # Return vizor
        return vizor
        

# Example usage
if __name__ == "__main__":
        
    try:

        # Import MIDI notes to send:
        from midi_queue_message.MIDINoteMessageOn import MIDINoteMessageOn   
        from midi_queue_message.MIDINoteMessageOff import MIDINoteMessageOff    
        from midi_queue_message.MIDIMessageChord import MIDIMessageChord    
        from midi_queue_message.MIDIMessageStop import MIDIMessageStop
        from midi_queue_message.MIDIMessageControl import MIDIMessageControl             

        # TODO: Probably need better way of selecting ports:
        outport = mido.open_output("E-MU XMidi1X1 Tab:E-MU XMidi1X1 Tab Out 20:0") 

        # initalize vizor for channels 1-16:
        vizor = MIDIQueueVizor.initChannels(outport)

        # Start queues
        eventLoopThread = vizor.start()

        # Create some messages to send
        '''
        msgs = [
           MIDIMessageChord(channel=0, tonic="C4", degrees=["1", "3", "5"], gate=1),
           MIDIMessageChord(channel=7, tonic="C4", degrees=["1"], gate=1),
           MIDIMessageStop(channel=0, gate=.25),
           MIDIMessageStop(channel=1, gate=.25),
           MIDIMessageChord(channel=0, tonic="C4", degrees=["1", "3b", "5"], transpose="1#", gate=1),
           MIDIMessageChord(channel=4, tonic="C4", degrees=["-1"], transpose="1#", gate=1),
           MIDIMessageStop(channel=0, gate=.25),
           MIDIMessageChord(channel=0, tonic="C4", degrees=["1", "3#", "5"], transpose="2", gate=1),
           MIDIMessageChord(channel=0, tonic="C4", degrees=["1", "3#", "5#"], transpose="2#", gate=1),
           MIDINoteMessageOn(channel=0, note="C3", gate=.25)
        ]
        '''

        '''
        msgs = [MIDINoteMessageOn(channel=7, note="C3")] 
        + MIDIMessageControl.easeIn(channel=7, cc=71, start=0, stop=127, gate=.25) 
        + [MIDINoteMessageOff(channel=7, note="C3")]
        '''
        msgs = [MIDINoteMessageOn(channel=7, note="C3")]  + MIDIMessageControl.linear(channel=7, cc=74, start=0, stop=127, gate=.025, steps=50) + MIDIMessageControl.linear(channel=7, cc=71, start=0, stop=127, gate=.025, steps=50) + [MIDINoteMessageOff(channel=7, note="C3")] 


        # Send Some messages
        for msg in msgs:
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



