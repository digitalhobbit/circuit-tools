#!/usr/bin/env python

"""Captures midi from Novation Circuit.

Writes a midi file with three tracks:
- Synth 1
- Synth 2
- Drums

This can be played as-is in midi players and imported into most DAW software
for further editing.

TODO:
- Determine tempo (e.g. based on initial cock ticks, before capture starts)
- Add command line parameters for sounds
- Make max patterns configurable and optional
"""

import mido
import os

# TODO: Make input name configurable
INPUT = 'Circuit'
OUTPUT_DIR = 'output'
OUTPUT_FILE = 'capture.mid'

# TODO: Make BPM configurable or infer from input
BPM = 120

TICKS_PER_BEAT = 24  # That's what Circuit uses

MAX_BARS = 8  # TODO: Make this configurable

CHANNEL_SYNTH1 = 0
CHANNEL_SYNTH2 = 1
CHANNEL_DRUMS = 9

CHANNEL_TO_INDEX = {
    CHANNEL_SYNTH1: 0,
    CHANNEL_SYNTH2: 1,
    CHANNEL_DRUMS: 2
}

# See here for other options: https://en.wikipedia.org/wiki/General_MIDI#Program_change_events
PROGRAM_SYNTH1 = 39  # Synth Bass 1
PROGRAM_SYNTH2 = 1   # Acoustic Grand Piano

# For some reason, Circuit uses drums 60-65, which mainly correspond to bongos and congas.
# We'll replace these with notes that correspond to the default Circuit drum sounds of
# kick, snare, open hi-hat, closed hi-hat respectively.
# See here for other options: https://en.wikipedia.org/wiki/General_MIDI#Percussion
DRUM_REPLACEMENTS = {
    60: 36,  # Bass Drum 1
    62: 38,  # Snare Drum 1
    64: 42,  # Closed Hi-hat
    65: 46,  # Open Hi-hat
}

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    mido.set_backend('mido.backends.rtmidi')

    with mido.MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT) as mid:
        tracks = [mid.add_track(name="Synth 1"),
            mid.add_track(name="Synth 2"),
            mid.add_track(name="Drums")]

        tracks[CHANNEL_SYNTH1].append(mido.Message('program_change', program=PROGRAM_SYNTH1))
        tracks[CHANNEL_SYNTH2].append(mido.Message('program_change', program=PROGRAM_SYNTH2))

        tempo = mido.bpm2tempo(BPM)
        meta = mido.MetaMessage('set_tempo', tempo=tempo)
        for track in tracks:
            track.append(meta)

        with mido.open_input(INPUT) as port:
            clocks = [0, 0, 0]
            capture = False
            total_ticks = 0
            print("Push 'Play' to start capture.")

            for msg in port:
                if msg.type == 'start':
                    print("Starting capture.")
                    capture = True
                elif msg.type == 'stop':
                    print("Stopping capture.")
                    capture = False
                    break
                elif capture:
                    if msg.type == 'clock':
                        clocks = [c + 1 for c in clocks]
                        total_ticks += 1
                        if total_ticks > TICKS_PER_BEAT * 4 * MAX_BARS:
                            print("End of song. Stopping capture.")
                            break
                    elif msg.type in ['note_on', 'note_off']:
                        index = CHANNEL_TO_INDEX[msg.channel]
                        track = tracks[index]

                        # Set message time to current clock count, then reset this track's clock
                        msg.time = clocks[index]
                        clocks[index] = 0

                        if msg.channel == CHANNEL_DRUMS:
                            msg.note = DRUM_REPLACEMENTS[msg.note]

                        print("Appending message: %s" % msg)
                        track.append(msg)

        mid.save("%s/%s" % (OUTPUT_DIR, OUTPUT_FILE))

    print("All done!")

#
# === Main ===
#

if __name__ == "__main__":
  main()
