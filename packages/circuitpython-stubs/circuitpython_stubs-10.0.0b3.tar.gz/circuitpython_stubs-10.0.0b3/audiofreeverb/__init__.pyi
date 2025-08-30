"""Support for audio freeverb effect

The `audiofreeverb` module contains classes to provide access to audio freeverb effects.

"""

from __future__ import annotations

import circuitpython_typing
import synthio

class Freeverb:
    """An Freeverb effect"""

    def __init__(
        self,
        roomsize: synthio.BlockInput = 0.5,
        damp: synthio.BlockInput = 0.5,
        mix: synthio.BlockInput = 0.5,
        buffer_size: int = 512,
        sample_rate: int = 8000,
        bits_per_sample: int = 16,
        samples_signed: bool = True,
        channel_count: int = 1,
    ) -> None:
        """Create a Reverb effect simulating the audio taking place in a large room where you get echos
           off of various surfaces at various times. The size of the room can be adjusted as well as how
           much the higher frequencies get absorbed by the walls.

           The mix parameter allows you to change how much of the unchanged sample passes through to
           the output to how much of the effect audio you hear as the output.

        :param synthio.BlockInput roomsize: The size of the room. 0.0 = smallest; 1.0 = largest.
        :param synthio.BlockInput damp: How much the walls absorb. 0.0 = least; 1.0 = most.
        :param synthio.BlockInput mix: The mix as a ratio of the sample (0.0) to the effect (1.0).
        :param int buffer_size: The total size in bytes of each of the two playback buffers to use
        :param int sample_rate: The sample rate to be used
        :param int channel_count: The number of channels the source samples contain. 1 = mono; 2 = stereo.
        :param int bits_per_sample: The bits per sample of the effect. Freeverb requires 16 bits.
        :param bool samples_signed: Effect is signed (True) or unsigned (False). Freeverb requires signed (True).

        Playing adding reverb to a synth::

          import time
          import board
          import audiobusio
          import synthio
          import audiofreeverb

          audio = audiobusio.I2SOut(bit_clock=board.GP20, word_select=board.GP21, data=board.GP22)
          synth = synthio.Synthesizer(channel_count=1, sample_rate=44100)
          reverb = audiofreeverb.Freeverb(roomsize=0.7, damp=0.3, buffer_size=1024, channel_count=1, sample_rate=44100, mix=0.7)
          reverb.play(synth)
          audio.play(reverb)

          note = synthio.Note(261)
          while True:
              synth.press(note)
              time.sleep(0.55)
              synth.release(note)
              time.sleep(5)"""
        ...

    def deinit(self) -> None:
        """Deinitialises the Freeverb."""
        ...

    def __enter__(self) -> Freeverb:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    roomsize: synthio.BlockInput
    """Apparent size of the room 0.0-1.0"""
    damp: synthio.BlockInput
    """How much the high frequencies are dampened in the area. 0.0-1.0"""
    mix: synthio.BlockInput
    """The rate the reverb mix between 0 and 1 where 0 is only sample and 1 is all effect."""
    playing: bool
    """True when the effect is playing a sample. (read-only)"""

    def play(
        self, sample: circuitpython_typing.AudioSample, *, loop: bool = False
    ) -> None:
        """Plays the sample once when loop=False and continuously when loop=True.
        Does not block. Use `playing` to block.

        The sample must match the encoding settings given in the constructor."""
        ...

    def stop(self) -> None:
        """Stops playback of the sample. The reverb continues playing."""
        ...
