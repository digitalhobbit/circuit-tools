# Captures midi from Novation Circuit.
# Writes a midi file with three tracks:
#   - Synth 1
#   - Synth 2
#   - Drums
#
# This can be played as-is in midi players and imported into most DAW software
# for further editing.
#
# TODO:
# - Determine tempo (e.g. based on initial cock ticks, before capture starts)
# - Figure out how to write tempo to the file
# - Add command line parameters for sounds

import mido

# TODO: Make input name configurable
INPUT = 'Circuit'

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

with mido.MidiFile(type=1, ticks_per_beat=24) as mid:
    tracks = [mid.add_track(name="Synth 1"),
        mid.add_track(name="Synth 2"),
        mid.add_track(name="Drums")]

    tracks[CHANNEL_SYNTH1].append(mido.Message('program_change', program=PROGRAM_SYNTH1))
    tracks[CHANNEL_SYNTH2].append(mido.Message('program_change', program=PROGRAM_SYNTH2))

    with mido.open_input(INPUT) as port:
        clocks = [0, 0, 0]
        capture = False
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
                elif msg.type in ['note_on', 'note_off']:
                    index = CHANNEL_TO_INDEX[msg.channel]
                    track = tracks[index]

                    # Set message time to current clock count, then reset this track's clock
                    msg.time = clocks[index]
                    clocks[index] = 0

                    if msg.channel == CHANNEL_DRUMS:
                        msg.note = DRUM_REPLACEMENTS[msg.note]

                    print ("Appending message: %s" % msg)
                    track.append(msg)

    mid.save('capture.mid')

print("All done!")
