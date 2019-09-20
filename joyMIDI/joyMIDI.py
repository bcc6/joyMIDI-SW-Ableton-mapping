from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SessionComponent import SessionComponent


class joyMIDI(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self.helloworld()
            self._create_session_control()

    def helloworld(self):
        self.log_message('helloworld')
        self.show_message('helloworld')

    def _create_session_control(self):
        self.session = SessionComponent(8, 2)
        self.session.set_offsets(0, 0)
        self.encoder = EncoderElement(MIDI_CC_TYPE, 0, 8, Live.MidiMap.MapMode.relative_binary_offset)
        self.encoder.add_value_listener(self._track_nav)
        self.set_highlighting_session_component(self.session)

    def _track_nav(self, value):
        value -= 64
        value = -value
        track_offset = self.session.track_offset()
        scene_offset = max(0, self.session.scene_offset() + value)
        self.session.set_offsets(track_offset, scene_offset)

    def disconnect(self):
        u"""Live -> Script
        Called right before we get disconnected from Live.
        """
        self.log_message('disconnect')
        self.show_message('disconnect')
