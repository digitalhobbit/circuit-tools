circuit-tools
=============
Various tools for the [Novation Circuit](https://us.novationmusic.com/circuit/circuit) groove box

## `capture.py`: Capture Circuit MIDI output into MIDI files

The Circuit is a wonderful little device, with some surprising capabilities. It has a solid step sequencer and several very decent synth engines. Most importantly, it's portable, tangible, colorful, and very easy and intuitive to use. All of this really lends itself to lots of creativity and happy accidents.

But still, this is only a groove box, and the sequencer is limited to chaining up to 8 one-bar patterns per track. So in order to complete full songs, my preferred workflow is to use the Circuit to generate patterns, then import these into my DAW as a starting point.

The `capture.py` tool makes this easy by capturing the Circuit's MIDI output and writing it to a MIDI file with three tracks, corresponding to Synth 1, Synth 2, and Drums respectively. This can be played as-is in any MIDI player, as well as imported into any DAW for further editing.

Most DAWs default to a reasonable set of instruments, so while the song likely won't sound exactly like it does on your Circuit, it should at least be playable, and you can tweak each instrument to your liking.

By default, the MIDI file uses Synth Bass 1 for Synth 1, Acoustic Grand Piano for Synth 2, and Kick, Snare, Close Hi-hat, and Open Hi-hat for Drum 1-4. This more or less matches Circuit's default instruments. Of course, if you significantly veer from this (e.g. by using Drum 1 for a Hi-hat sound instead of Kick), the resulting MIDI file won't be a close representation.

Some DAWs (such as Bitwig) don't handle the drum track correctly. You'll need to load a suitable drum instrument (e.g. Bitwig's drum kit) to hear the expected drums.


### Installation
capture.py uses [Mido](https://github.com/olemb/mido), a platform independent Python MIDI library that wraps either PortMidi, RtMidi, or PYgame. I have only tested this in OSX, using the [Homebrew](http://brew.sh/) version of Python and RtMidi. Your mileage may vary with other combinations...

Install mido and rtmidi:

    brew install rtmidi
    pip install python-rtmidi mido

Clone the circuit-tools repository:

    git clone https://github.com/digitalhobbit/circuit-tools.git
    cd circuit-tools

### Usage
1. Connect your Circuit's USB cable to your computer. It should show up on your computer as a MIDI device named "Circuit". (On OSX, you can verify this in the Audio MIDI Setup tool.)

2. Run `./capture.py`

3. At the prompt, hit your Circuit's "Play" button. When you're done, hit "Play" again to stop.

4. That's it! You should now see a file called "capture.mid". Play it in your MIDI player or drag it into your DAW to hear it.
