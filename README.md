circuit-tools
=============
Various tools for the [Novation Circuit](https://us.novationmusic.com/circuit/circuit) groove box

## `capture.py`: Capture Circuit MIDI output into MIDI files

The Circuit is a wonderful little device, with some surprising capabilities. It has a solid step sequencer and several very decent synth engines. Most importantly, it's portable, tangible, colorful, and very easy and intuitive to use. All of this really lends itself to lots of creativity and happy accidents.

But still, this is only a groove box, and the sequencer is limited to chaining up to 8 one-bar patterns per track. While recording audio into your DAW for further editing is one option, my preferred workflow to complete full songs is to use the Circuit to create MIDI patterns, then import these into my DAW as a starting point.

The `capture.py` tool makes this easy by capturing the Circuit's MIDI output and writing it to a MIDI file with three tracks, corresponding to Synth 1, Synth 2, and Drums respectively. This can be played as-is in any MIDI player, as well as imported into any DAW for further editing.

Most DAWs default to a reasonable set of instruments, so while the song likely won't sound exactly like it does on your Circuit, it should at least be playable, and you can tweak each instrument to your liking.

By default, the MIDI file uses Synth Bass 1 for Synth 1, Acoustic Grand Piano for Synth 2, and Kick, Snare, Close Hi-hat, and Open Hi-hat for Drum 1-4. This more or less matches Circuit's default instruments. Of course, if you significantly veer from this (e.g. by using Drum 1 for a Hi-hat sound instead of Kick), the resulting MIDI file won't be a close representation.

Some DAWs (such as Bitwig) don't handle the drum track correctly. You'll need to load a suitable drum instrument (e.g. Bitwig's drum kit) to hear the expected drums.

`capture.py` provides several command line options to change the way it handles drums in order to improve compatibility with all DAWs. See Advanced Options below.


### Installation
capture.py uses [Mido](https://github.com/olemb/mido), a platform independent Python MIDI library that wraps either PortMidi, RtMidi, or PYgame. While it should in principle work in OSX, Linux, and Windows, I have only tested this in OSX, using the [Homebrew](http://brew.sh/) version of Python and RtMidi. Your mileage may vary with other combinations...

1. Install mido and rtmidi (OSX):

        brew install rtmidi
        pip install python-rtmidi mido

2. Download and unzip the [circuit-tools files](https://github.com/digitalhobbit/circuit-tools/archive/master.zip).

3. Open a Terminal window and cd into the circuit-tools directory you unzipped.


### Usage
1. Connect your Circuit's USB cable to your computer. It should show up on your computer as a MIDI device named "Circuit". (On OSX, you can verify this in the Audio MIDI Setup tool.)

2. Run `./capture.py`

3. At the prompt, hit your Circuit's "Play" button. When you're done, hit "Play" again to stop.

4. That's it! You should now see a file called `capture.mid` in the `output` directory. Play it in your MIDI player or drag and drop it into your DAW to hear it.


### Advanced Options
A few of the options are described below. You can run `./capture.py -h` to see all available options.

* `-t` or `--tempo`: Specify the tempo in BPM. Otherwise, the tempo is determined automatically during capturing based on the MIDI clock (but note that it may not be entirely accurate unless you play a full 8 bars).

* `-b` or `--bars`: Specify the number of bars to capture (default: 8). Specify `0` to continue capturing until you hit the "Play" button to stop.

* `-d` or `--drums`: Specify the drum scheme to use. Pick what works best for your DAW. Current options:
    * `gm`: General MIDI. Creates notes that map to General MIDI bass drum, snare drum, closed hi-hat, and open hi-hat. Resulting MIDI files should play fine in any MIDI player, as well as DAW-native or VST drum instruments that use these mappings, such as Logic Pro (both Drum Kit and Ultrasound) or Rob Papen Punch.
    * `gm2`: Identical to gm, except for using Pedal Hi-Hat instead of Closed Hi-Hat. Intended for use with Native Instruments Battery, which mostly matches General MIDI notes, except for placing the Open Hi-Hat sound on the Pedal Hi-Hat note.
    * `c1up`: This scheme uses semitones from C1 (i.e. C1, C#1, D1, D#1). Many drum instruments (such as FXpansion Tremor or Bitwig's built-in Drum Machine) map these to kick, snare, closed hi-hat, and open hi-hat respectively. Note that files with this drum scheme won't play correctly in regular MIDI players.

### Help
Please file an issue for bugs or feature requests. Pull requests are welcome, as well. :)
