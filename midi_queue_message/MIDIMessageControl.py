# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
from typing import Union, List                                     # For annotating a value that maybe of more than one possible type
import asyncio                                                     # For using async operations (like sleep)
import mido                                                        # For sending MIDI messages
from midi_queue_message.main import MIDIQueueMessage               # Base class we are extending from
from midi_queue_message.MIDINoteMessage import MIDINoteMessage     # Using static methods for note value lookup
from midi_queue.main import MIDIQueue                              # For annotating MIDIQueue type in "call" magic method
import numpy as np                                                 # For calculating a cubic bezier curve used by easing functions 

class MIDIMessageControl (MIDIQueueMessage):

    """Implements how to process a "control_change" MIDI message with optional gate delay"""

    def __init__(self, channel : int , cc :int, value : int, gate :Union[int, float, None] = None):
        super().__init__(channel=channel)
        self._cc = cc                     # Control Change Parameter (which is device specifc)
        self._value = value               # Value we are sending to that control change parameter
        self._gate = gate                 # Gate delay is for "rests" between additional control changes
        self._msgType = "control_change"  # Setting Message type, mainly for debugging purposes:

    #################
    # Magic Methods #
    #################

    async def __call__(self, queue: "MIDIQueue" = None):

        try:

            """Implements how to process a CONTROL_CHANGE MIDI message with optional gate delay"""
            # NOTE: If no queue is set, we print the message when called
            # Initialize and send message if queue is set:
            if queue is not None and queue.active is True:
                message = mido.Message('control_change', control=self._cc, value=self._value, channel=self.channel)
                queue.vizor.send(message)
            else:
                print(self)

            # "Rest" between additional control changes or sent messages:
            if self._gate is not None:
                await asyncio.sleep(self._gate) 

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    ##################
    # Static Methods #
    ##################

    @staticmethod
    def cc_on(channel : int, cc : int, gate :Union[int, float, None] = None):
        """Implements typical togge ON cc param by sending a value of 127"""
        return MIDIMessageControl(channel=channel, cc=cc, value=127, gate=gate)

    @staticmethod
    def cc_off(channel : int, cc : int, gate :Union[int, float, None] = None):
        """Implements typical togge OFF cc param by sending a value of 0"""
        return MIDIMessageControl(channel=channel, cc=cc, value=0, gate=gate)

    @staticmethod
    def cc_sweep(channel : int, cc : int, values : List[int], gate :Union[int, float, None] = None):
        """Creates a list of MIDIMessageControl message from a list of values for a specific cc param"""
        msgs = []
        for value in values:
            msg = MIDIMessageControl(channel=channel, cc=cc, value=value, gate=gate)
            msgs.append(msg)
        return msgs

    @staticmethod
    def cubic_bezier_midi_cc(x1, y1, x2, y2, start_value, end_value, points=None):
        """
        Generates a cubic Bezier easing function for MIDI CC values based on CSS-like cubic-bezier(x1, y1, x2, y2).
        
        :param x1: Control point 1 (x)
        :param y1: Control point 1 (y)
        :param x2: Control point 2 (x)
        :param y2: Control point 2 (y)
        :param start_value: Starting MIDI CC value (0-127)
        :param end_value: Ending MIDI CC value (0-127)
        :param points : Specific number of points to calculate the curve with, where the more points means the smoother the curve
        :return: List of integer values representing the eased MIDI CC values
        """
        # Ensure correct handling when start_value is greater than end_value (reversed case)
        reverse = start_value > end_value

        num_points = points if points is not None else abs(end_value - start_value)  # Number of steps
        t_values = np.linspace(0, 1, num_points)

        bezier_values = []
        for t in t_values:
            # Calculate the Bezier curve for both x and y axes
            x = (1 - t)**3 * 0 + 3 * (1 - t)**2 * t * x1 + 3 * (1 - t) * t**2 * x2 + t**3 * 1
            y = (1 - t)**3 * 0 + 3 * (1 - t)**2 * t * y1 + 3 * (1 - t) * t**2 * y2 + t**3 * 1
            
            # If reversed, flip the t-axis by using 1 - t
            if reverse:
                midi_value = int(np.clip(end_value + (1 - y) * (start_value - end_value), 0, 127))
            else:
                midi_value = int(np.clip(start_value + y * (end_value - start_value), 0, 127))
            
            bezier_values.append(midi_value)

        return bezier_values

    '''
    @staticmethod
    def cubic_bezier_midi_cc(x1, y1, x2, y2, start_value, end_value, points = None):
        """
        Generates a cubic Bezier easing function for MIDI CC values based on CSS-like cubic-bezier(x1, y1, x2, y2).
        
        :param x1: Control point 1 (x)
        :param y1: Control point 1 (y)
        :param x2: Control point 2 (x)
        :param y2: Control point 2 (y)
        :param start_value: Starting MIDI CC value (0-127)
        :param end_value: Ending MIDI CC value (0-127)
        :param points : Specific number of points to calculate the curve with, where the more points means the smoother the curve
        :return: List of integer values representing the eased MIDI CC values
        """
        num_points = points if points is not None else abs(end_value - start_value)  # Number of steps
        t_values = np.linspace(0, 1, num_points)
        
        bezier_values = []
        for t in t_values:
            # Calculate the Bezier curve for both x and y axes
            x = (1 - t)**3 * 0 + 3 * (1 - t)**2 * t * x1 + 3 * (1 - t) * t**2 * x2 + t**3 * 1
            y = (1 - t)**3 * 0 + 3 * (1 - t)**2 * t * y1 + 3 * (1 - t) * t**2 * y2 + t**3 * 1
            
            # Map the cubic bezier output (y) to the MIDI CC value range
            midi_value = int(np.clip(start_value + y * (end_value - start_value), 0, 127))
            bezier_values.append(midi_value)

        return bezier_values
    '''


        
    @staticmethod
    def easeIn(channel : int, cc : int, start : int = 0, stop: int = 127, gate :Union[int, float, None] = None, steps : int =None, debug : bool = False ):
        """Defines an 'ease-in` easing function for 'sweeping' a cc param with"""
        values = MIDIMessageControl.cubic_bezier_midi_cc(0.42, 0, 1.0, 1.0, start, stop, steps)
        return values if debug is True else MIDIMessageControl.cc_sweep(channel=channel, cc=cc, values=values, gate=gate)
    
    @staticmethod
    def easeOut(channel : int, cc : int, start : int = 0, stop: int = 127, gate :Union[int, float, None] = None, steps : int =None, debug : bool = False ):
        """Defines an 'ease-out` easing function for 'sweeping' a cc param with"""
        values = MIDIMessageControl.cubic_bezier_midi_cc(0, 0, 0.58, 1.0, start, stop, steps)
        return values if debug is True else MIDIMessageControl.cc_sweep(channel=channel, cc=cc, values=values, gate=gate)
    
    @staticmethod
    def easeInOut(channel : int, cc : int, start : int = 0, stop: int = 127, gate :Union[int, float, None] = None, steps : int =None, debug : bool = False  ):
        """Defines an 'ease-in-out` easing function for 'sweeping' a cc param with"""
        values = MIDIMessageControl.cubic_bezier_midi_cc(0.42, 0, 0.58, 1.0, start, stop, steps)
        return values if debug is True else MIDIMessageControl.cc_sweep(channel=channel, cc=cc, values=values, gate=gate)
    
    @staticmethod
    def linear(channel : int, cc : int, start : int = 0, stop: int = 127, gate :Union[int, float, None] = None, steps : int =None, debug : bool = False  ):
        """Defines a 'linear` easing function for 'sweeping' a cc param with"""
        values = MIDIMessageControl.cubic_bezier_midi_cc(0.0, 0.0, 1.0, 1.0, start, stop, steps)
        return values if debug is True else MIDIMessageControl.cc_sweep(channel=channel, cc=cc, values=values, gate=gate)
    
    @staticmethod
    def easeInOutSine(channel : int, cc : int, start : int = 0, stop: int = 127, gate :Union[int, float, None] = None, steps : int =None, debug : bool = False  ):
        """Defines a 'ease-in-out-sine` easing function for 'sweeping' a cc param with"""
        values = MIDIMessageControl.cubic_bezier_midi_cc(0.37, 0, 0.63, 1, start, stop, steps)
        return values if debug is True else MIDIMessageControl.cc_sweep(channel=channel, cc=cc, values=values, gate=gate)
    
 
# Example usage
if __name__ == "__main__":

    '''
    import asyncio # We need to import this so we can call the async "call" magic method of an initialized MIDINoteMessage

    # Print messages by "calling them":
    async def main(messages):
        for message in messages:
            await message();

    # Create some message:
    notes = [
        MIDIMessageControl(channel=0, cc=71, value=64),          # TB-03 Resonance
        MIDIMessageControl(channel=0, cc=74, value=80, gate=1),  # TB-03 Cut off frequency
        MIDIMessageControl(channel=0, cc=74, value=127, gate=1), # TB-03 Cut off frequency
    ]

    # Call notes:
    asyncio.run(main(notes))
    '''

    msgs = MIDIMessageControl.easeIn(channel=0, cc=71, start=127, stop=0, steps=100, debug=True)
    print(msgs)

