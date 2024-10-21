# Add the path to the parent directory to sys.path:
import sys
import os
modules_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(modules_dir_path)

# Dependencies
import xml.etree.ElementTree as ET  # For parsing XML
from midi_cast_xml.MIDICastXMLNote import MIDICastXMLNote
from midi_cast_xml.MIDICastXMLChord import MIDICastXMLChord
from midi_cast_xml.MIDICastXMLRest import MIDICastXMLRest

class MIDICastXML:

    '''Transforms XML into MIDIQueueMessage objects '''

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, xml : str):
        self.root = xml   # Stores root element of parsed tree

    ##############
    # Properties #
    ##############


    @property
    def root(self) -> ET.Element:
        """GETTER for XML tree root element"""
        return self._root
    
    @root.setter
    def root(self, xml : str) -> None:
        """SETTER for XML tree root element"""
        self._root = ET.fromstring(xml)

    ####################
    # Instance Methods #
    ####################

    
    def transform(self, debug : bool = False):
        """Transforms the stored XML tree into a list of MIDIQueueMessage"""
        result = []
        for elem in self.root.iter():
            if debug is True:
                elemProps = {}
                elemProps["tag"] = elem.tag
                elemProps["attributes"] = elem.attrib
                result.append(elemProps)
            else:
                if elem.tag == "note":
                    MIDICastXMLNote.init(elem, result)
                if elem.tag == "chord":
                    MIDICastXMLChord.init(elem, result)
                if elem.tag == "rest":
                     MIDICastXMLRest.init(elem, result)
        return result
    
    def send(self, vizor):
        """Transform stored XML into a list of MIDIQueMessage instance and then sends them to the given vizor"""
        messages = self.transform()
        for message in messages:
            vizor.relay(message)

    ##################
    # Static Methods #
    ##################

    @staticmethod
    def load(filename):
        """Loads XML from file to initialize MIDICastXML with"""
        with open(filename, 'r') as file:
            xml = file.read()
        return MIDICastXML(xml)
    
    @staticmethod
    def init(xml, vizor):
        """Initializes an instance of MIDICastXML then transforms xml and passes messages to given vizor"""
        midiCastXML = MIDICastXML(xml)
        midiCastXML.send(vizor)

# Example usage
if __name__ == "__main__":

    # Load in example as our test XML:
    xmlFile = "./example.xml"
    debug = False
    xml = MIDICastXML.load(xmlFile)

    # Determine if we are going to print transformed messages or send messages to a vizor instance:
    if debug is True:
        
        # Transform and print XML as a list of MIDIQueueMessages:
        result = xml.transform()
        print(result)

    else:

        try:
        
            # Import MIDI notes to send:
            from midi_queue_vizor.main import MIDIQueueVizor
            import mido                                             
        
            # TODO: Probably need better way of selecting ports:
            outport = mido.open_output("E-MU XMidi1X1 Tab:E-MU XMidi1X1 Tab Out 20:0") 

            # initalize vizor for channels 1-16:
            vizor = MIDIQueueVizor.initChannels(outport)

            # Start queues
            eventLoopThread = vizor.start()

            # Transforms XML into message and then send them vizorL
            xml.send(vizor)

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