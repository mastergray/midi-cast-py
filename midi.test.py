import mido
import time


# List available input ports
input_ports = mido.get_input_names()
print("Available input ports:", input_ports)

# List available output ports
output_ports = mido.get_output_names()
print("Available output ports:", output_ports)

# TODO: Probably need better way of selecting ports:
inport = mido.open_input("E-MU XMidi1X1 Tab:E-MU XMidi1X1 Tab Out 20:0") 
outport = mido.open_output("E-MU XMidi1X1 Tab:E-MU XMidi1X1 Tab Out 20:0") 

# Test message to middle C (C4 or 60) on Channel 1 (or 0?):
note = 60
channel=0
velocity = 127
gate = 1

# Create messages:
noteOn = mido.Message("note_on", channel=channel, note=note, velocity=velocity)
noteOff = mido.Message("note_off", channel=channel, note=note, velocity=velocity)

# See what happens"
print("Sending...")
outport.send(noteOn)
time.sleep(gate)
outport.send(noteOff)
print("Done.")
