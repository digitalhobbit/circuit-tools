#!/usr/bin/env python

"""Captures midi from Novation Circuit.

Writes a midi file with three tracks:
- Synth 1
- Synth 2
- Drums

This can be played as-is in midi players and imported into most DAW software
for further editing.

TODO:
- Optionally output multiple MIDI files to cover all drum variations (e.g. perhaps
  allow multiple format params, default = general midi)
- Add command line parameters for synth sounds
"""

import argparse
import mido
import os
import time

INPUT = 'Circuit'
OUTPUT_FILE = './output/capture.mid'

SONG_NAME = "Circuit Import"

TICKS_PER_BEAT = 24  # That's what Circuit uses
MAX_BARS = 8

CHANNEL_SYNTH1 = 0
CHANNEL_SYNTH2 = 1
CHANNEL_DRUMS = 9

CHANNEL_TO_INDEX = {
    CHANNEL_SYNTH1: 0,
    CHANNEL_SYNTH2: 1,
    CHANNEL_DRUMS: 2
}

PROGRAM_SYNTH1 = 39  # Synth Bass 1
PROGRAM_SYNTH2 = 1   # Acoustic Grand Piano

# Circuit uses drums 60, 62, 64, 65 (C5, D5, E5, F5), which map neither to meaningful General MIDI
# sounds, nor to typical native DAW or VST drum instruments. We will therefore translate them to
# meaningful notes according to the chosen scheme, in order to work well with your setup.
# Consistent with the default Circuit drum sounds, each scheme maps to notes that typically
# represent bass drum, snare drum, closed hi-hat, and open hi-hat respectively. Of course,
# the exact sounds may vary, depending on your drum kit.
# See here for other options: https://en.wikipedia.org/wiki/General_MIDI#Percussion
DRUM_REPLACEMENTS = {
    # The scheme below uses standard General MIDI drum sounds. Resulting MIDI files should play
    # fine in any MIDI player, as well as DAW-native or VST drum instruments that use these
    # mappings, such as Logic Pro (both Drum Kit and Ultrasound) or Rob Papen Punch.
    'gm': {
        60: 36,  # Bass Drum 1
        62: 38,  # Snare Drum 1
        64: 42,  # Closed Hi-hat
        65: 46,  # Open Hi-hat
    },
    # Identical to gm, except for Pedal Hi-Hat instead of Closed Hi-Hat. Intended for use with
    # Native Instruments Battery, which mostly matches General MIDI notes, except for placing the
    # Open Hi-Hat sound on the Pedal Hi-Hat note.
    'gm2': {
        60: 36,  # Bass Drum 1
        62: 38,  # Snare Drum 1
        64: 44,  # Pedal Hi-Hat
        65: 46,  # Open Hi-hat
    },
    # This scheme uses semitones from C1 (i.e. C1, C#1, D1, D#1). Many drum instruments (such as
    # FXpansion Tremor or Bitwig's built-in Drum Machine) map these to kick, snare, closed hi-hat,
    # and open hi-hat respectively.
    # Note that files with this drum scheme won't play correctly in regular MIDI players.
    'c1up': {
        60: 36,  # C1
        62: 37,  # C#1
        64: 38,  # D1
        65: 39,  # D#1
    }
}


def main():
    parser = argparse.ArgumentParser(
        description="Capture MIDI from Novation Circuit and write to .mid file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true', help="Verbose output")
    parser.add_argument('-i', '--input', action='store', default=INPUT,
                        help="MIDI Input")
    parser.add_argument('-o', '--output', action='store', default=OUTPUT_FILE,
                        help="Output filename")
    parser.add_argument('-t', '--tempo', type=int, action='store', help="Tempo in BPM")
    parser.add_argument('-b', '--bars', type=int, action='store', default=MAX_BARS,
                        help="Max # bars (0 = until Stop)")
    parser.add_argument('-d', '--drums', action='store', choices=['gm', 'gm2', 'c1up'], default='gm',
                        help="Drum notes to generate. gm = General MIDI, gm2 = General MIDI NI Battery optimized, c1up = semitones from C1")
    args = parser.parse_args()

    circuit_capture = CircuitCapture(args.verbose, args.input, args.output, args.tempo,
                                     args.bars, args.drums)
    circuit_capture.capture()


class CircuitCapture:
    def __init__(self, verbose, input, output, tempo_bpm, bars, drums):
        self.verbose = verbose
        self.input = input
        self.output = output
        self.tempo_bpm = tempo_bpm
        self.bars = bars
        self.drums = drums

        self.capturing = False
        self.final_tick = False
        # Start clocks at -1 to account for Circuit's leading clock message after start
        self.clocks = [-1, -1, -1]
        self.total_ticks = 0


    def capture(self):
        output_dir = os.path.dirname(self.output)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        mido.set_backend('mido.backends.rtmidi')

        with mido.MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT) as mid:
            # Create tracks
            self.tempo_map_track = mid.add_track(name=SONG_NAME)
            self.tracks = [mid.add_track(name="Synth 1"),
                mid.add_track(name="Synth 2"),
                mid.add_track(name="Drums")]

            # Set synth instruments
            self.tracks[CHANNEL_SYNTH1].append(mido.Message('program_change', program=PROGRAM_SYNTH1))
            self.tracks[CHANNEL_SYNTH2].append(mido.Message('program_change', program=PROGRAM_SYNTH2))

            with mido.open_input(self.input) as port:
                print("Push 'Play' to start capture.")
                for msg in port:
                    if not self.process_message(msg):
                        self.capturing = False
                        break

            # Figure out BPM, either from command line argument or from actual timing
            bpm = self.tempo_bpm
            if not bpm:
                end_time = time.time()
                delta = end_time - self.start_time
                beats = self.total_ticks / TICKS_PER_BEAT
                bpm = int(round(beats * 60 / delta))
            print("BPM: %d" % bpm)

            # Write tempo and time signature to tempo map track
            self.tempo_map_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
            self.tempo_map_track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))

            mid.save(self.output)
            print("All done!")


    # Returns false when capturing should be stopped.
    def process_message(self, msg):
        if msg.type == 'start':
            print("Starting capture.")
            self.capturing = True
            self.start_time = time.time()
        elif msg.type == 'stop':
            print("Stopping capture.")
            return False
        elif self.capturing:
            if msg.type == 'clock':
                self.clocks = [c + 1 for c in self.clocks]
                self.total_ticks += 1
                if self.verbose:
                    print("Ticks: %d" % self.total_ticks)
                if self.bars > 0 and self.total_ticks > TICKS_PER_BEAT * 4 * self.bars:
                    if self.final_tick:
                        # We've already processed the final tick => stop capture
                        return False
                    else:
                        self.final_tick = True
                        print("End of song. Stopping capture.")
            elif msg.type in ['note_on', 'note_off']:
                # During final tick, only accept note_off messages
                if msg.type == 'note_off' or not self.final_tick:
                    self.replace_drums(msg)
                    self.update_time(msg)
                    self.append_to_track(msg)
        return True

    # Replace drums based on chosen scheme, if the message is on the drum channel
    def replace_drums(self, msg):
        if msg.channel == CHANNEL_DRUMS:
            msg.note = DRUM_REPLACEMENTS[self.drums][msg.note]

    # Set message time to current clock count, then reset this track's clock
    def update_time(self, msg):
        msg.time = self.clocks[self._index(msg)]
        self.clocks[self._index(msg)] = 0

    def append_to_track(self, msg):
        print("Appending message: %s" % msg)
        track = self.tracks[self._index(msg)]
        track.append(msg)

    def _index(self, msg):
        return CHANNEL_TO_INDEX[msg.channel]

#
# === Main ===
#

if __name__ == "__main__":
  main()
