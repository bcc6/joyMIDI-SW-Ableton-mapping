# Soundless studio
# Ozzy Chiu
# 2019.09.28
# Features: Transport, Mixer, Session
from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonSliderElement import ButtonSliderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.Util import index_if
from itertools import chain


SEND_STEPS = 20
PAN_STEPS = 20
VOLUME_STEPS = 20


class joyMIDI(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self.setup_transport()
            self.setup_mixer()
            self.setup_session()

    def setup_transport(self):
        # elements
        self.play_button   = ButtonElement(True, MIDI_NOTE_TYPE, 0, 93)
        self.stop_button   = ButtonElement(True, MIDI_NOTE_TYPE, 0, 94)
        self.record_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, 95)
        # transport
        self.transport = TransportComponent()
        self.transport.set_play_button(self.play_button)
        self.transport.set_stop_button(self.stop_button)
        self.transport.set_record_button(self.record_button)

    def setup_mixer(self):
        # elements
        self.mute_button        = ButtonElement(True, MIDI_NOTE_TYPE, 0, 92)   # tracks, return_tracks
        self.solo_button        = ButtonElement(True, MIDI_NOTE_TYPE, 0, 84)   # tracks, return_tracks
        self.arm_button         = ButtonElement(True, MIDI_NOTE_TYPE, 0, 85)   # tracks
        self.senda_up_button    = ButtonElement(True, MIDI_NOTE_TYPE, 0, 96)   # tracks, return_tracks
        self.senda_down_button  = ButtonElement(True, MIDI_NOTE_TYPE, 0, 88)   # tracks, return_tracks
        self.sendb_up_button    = ButtonElement(True, MIDI_NOTE_TYPE, 0, 97)   # tracks, return_tracks
        self.sendb_down_button  = ButtonElement(True, MIDI_NOTE_TYPE, 0, 89)   # tracks, return_tracks
        self.pan_up_button      = ButtonElement(True, MIDI_NOTE_TYPE, 0, 98)   # tracks, return_tracks, master_track
        self.pan_down_button    = ButtonElement(True, MIDI_NOTE_TYPE, 0, 90)   # tracks, return_tracks, master_track
        self.volume_up_button   = ButtonElement(True, MIDI_NOTE_TYPE, 0, 99)   # tracks, return_tracks, master_track
        self.volume_down_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, 91)   # tracks, return_tracks, master_track
        self.track_nav_encoder  = EncoderElement(MIDI_CC_TYPE, 0, 14, Live.MidiMap.MapMode.relative_binary_offset)
        # mixer
        self.mixer = MixerComponent(7, 2)
        self.mixer.selected_strip().set_mute_button(self.mute_button)
        self.mixer.selected_strip().set_solo_button(self.solo_button)
        self.mixer.selected_strip().set_arm_button(self.arm_button)
        # send A/B, pan, volume
        self.senda_up_button.add_value_listener(self.on_senda_up_changed)
        self.senda_down_button.add_value_listener(self.on_senda_down_changed)
        self.sendb_up_button.add_value_listener(self.on_sendb_up_changed)
        self.sendb_down_button.add_value_listener(self.on_sendb_down_changed)
        self.pan_up_button.add_value_listener(self.on_pan_up_changed)
        self.pan_down_button.add_value_listener(self.on_pan_down_changed)
        self.volume_up_button.add_value_listener(self.on_volume_up_changed)
        self.volume_down_button.add_value_listener(self.on_volume_down_changed)
        # nav
        self.track_nav_encoder.add_value_listener(self.on_mixer_track_nav)

    def on_senda_up_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.sends[0]
            param.value = max(param.min, min(param.max, param.value + ((param.max - param.min) / SEND_STEPS)))

    def on_senda_down_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.sends[0]
            param.value = max(param.min, min(param.max, param.value - ((param.max - param.min) / SEND_STEPS)))

    def on_sendb_up_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.sends[1]
            param.value = max(param.min, min(param.max, param.value + ((param.max - param.min) / SEND_STEPS)))

    def on_sendb_down_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.sends[1]
            param.value = max(param.min, min(param.max, param.value - ((param.max - param.min) / SEND_STEPS)))

    def on_pan_up_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.panning
            param.value = max(param.min, min(param.max, param.value + ((param.max - param.min) / PAN_STEPS)))

    def on_pan_down_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.panning
            param.value = max(param.min, min(param.max, param.value - ((param.max - param.min) / PAN_STEPS)))

    def on_volume_up_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.volume
            param.value = max(param.min, min(param.max, param.value + ((param.max - param.min) / VOLUME_STEPS)))

    def on_volume_down_changed(self, value):
        if value > 0:
            param = self.song().view.selected_track.mixer_device.volume
            param.value = max(param.min, min(param.max, param.value - ((param.max - param.min) / VOLUME_STEPS)))

    def on_mixer_track_nav(self, value):
        move = -1 if value > 64 else +1
        # get tracks-info
        tracks = self.song().tracks
        return_tracks = self.song().return_tracks
        master_track = self.song().master_track
        all_tracks = list(chain(tracks, return_tracks)); all_tracks.append(master_track)
        num_tracks = len(tracks)
        num_return_tracks = len(return_tracks)
        num_master_track = 1
        num_all_tracks = num_tracks + num_return_tracks + num_master_track
        # update selected-track
        index = index_if(lambda t: t==self.song().view.selected_track, all_tracks)
        index += move
        index = min(max(index, 0), num_all_tracks-1)
        self.song().view.selected_track = all_tracks[index]

    def setup_session(self):
        num_tracks = 7
        num_scenes = 1
        track_offset = 0
        scene_offset = 0
        # elements
        self.clip_launch_buttons = ButtonMatrixElement(rows=[
            [ButtonElement(True, MIDI_NOTE_TYPE, 0, 76+i) for i in range(num_tracks)]
        ])
        self.clip_stop_buttons = [
            ButtonElement(True, MIDI_NOTE_TYPE, 0, 68+i) for i in range(num_tracks)
        ]
        self.scene_launch_buttons = ButtonMatrixElement(rows=[
            [ButtonElement(True, MIDI_NOTE_TYPE, 0, 83+i) for i in range(num_scenes)]
        ])
        self.scene_stop_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, 75)
        self.session_scene_nav_encoder = EncoderElement(MIDI_CC_TYPE, 0, 15, Live.MidiMap.MapMode.relative_binary_offset)
        # session
        self.session = SessionComponent(num_tracks, num_scenes)
        self.session.set_offsets(track_offset, scene_offset)
        self.session.add_offset_listener(self.on_session_offset_changed)
        self.set_highlighting_session_component(self.session)
        # clips
        self.session.set_clip_launch_buttons(self.clip_launch_buttons)
        self.session.set_stop_track_clip_buttons(self.clip_stop_buttons)
        self.session.set_scene_launch_buttons(self.scene_launch_buttons)
        self.session.set_stop_all_clips_button(self.scene_stop_button)
        # nav
        self.session_scene_nav_encoder.add_value_listener(self.on_session_scene_nav)

    def on_session_offset_changed(self):
        pass

    def on_session_scene_nav(self, value):
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
