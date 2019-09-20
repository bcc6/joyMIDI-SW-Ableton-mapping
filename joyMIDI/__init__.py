from __future__ import absolute_import, print_function, unicode_literals
from _Framework.Capabilities import *
from .joyMIDI import joyMIDI

def create_instance(c_instance):
    return joyMIDI(c_instance)

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=1792, product_ids=[
                       	257], model_name='joyMIDI'), 
     	PORTS_KEY: [
	            inport(props=[NOTES_CC, REMOTE, SCRIPT]),
	            outport(props=[NOTES_CC, REMOTE, SCRIPT])]}