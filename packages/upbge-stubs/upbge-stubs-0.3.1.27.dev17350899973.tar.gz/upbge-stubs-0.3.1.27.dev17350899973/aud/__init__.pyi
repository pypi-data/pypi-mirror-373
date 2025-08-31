"""


Audio System (aud)
******************

Audaspace (pronounced "outer space") is a high level audio library.


Basic Sound Playback
====================

This script shows how to use the classes: :class:`Device`, :class:`Sound` and
:class:`Handle`.

.. code::

  import aud

  device = aud.Device()
  # Load sound file (it can be a video file with audio).
  sound = aud.Sound('music.ogg')

  # Play the audio, this return a handle to control play/pause.
  handle = device.play(sound)
  # If the audio is not too big and will be used often you can buffer it.
  sound_buffered = aud.Sound.cache(sound)
  handle_buffered = device.play(sound_buffered)

  # Stop the sounds (otherwise they play until their ends).
  handle.stop()
  handle_buffered.stop()

:data:`AP_LOCATION`

:data:`AP_ORIENTATION`

:data:`AP_PANNING`

:data:`AP_PITCH`

:data:`AP_PITCH_SCALE`

:data:`AP_TIME_STRETCH`

:data:`AP_VOLUME`

:data:`CHANNELS_INVALID`

:data:`CHANNELS_MONO`

:data:`CHANNELS_STEREO`

:data:`CHANNELS_STEREO_LFE`

:data:`CHANNELS_SURROUND4`

:data:`CHANNELS_SURROUND5`

:data:`CHANNELS_SURROUND51`

:data:`CHANNELS_SURROUND61`

:data:`CHANNELS_SURROUND71`

:data:`CODEC_AAC`

:data:`CODEC_AC3`

:data:`CODEC_FLAC`

:data:`CODEC_INVALID`

:data:`CODEC_MP2`

:data:`CODEC_MP3`

:data:`CODEC_OPUS`

:data:`CODEC_PCM`

:data:`CODEC_VORBIS`

:data:`CONTAINER_AAC`

:data:`CONTAINER_AC3`

:data:`CONTAINER_FLAC`

:data:`CONTAINER_INVALID`

:data:`CONTAINER_MATROSKA`

:data:`CONTAINER_MP2`

:data:`CONTAINER_MP3`

:data:`CONTAINER_OGG`

:data:`CONTAINER_WAV`

:data:`DISTANCE_MODEL_EXPONENT`

:data:`DISTANCE_MODEL_EXPONENT_CLAMPED`

:data:`DISTANCE_MODEL_INVALID`

:data:`DISTANCE_MODEL_INVERSE`

:data:`DISTANCE_MODEL_INVERSE_CLAMPED`

:data:`DISTANCE_MODEL_LINEAR`

:data:`DISTANCE_MODEL_LINEAR_CLAMPED`

:data:`FORMAT_FLOAT32`

:data:`FORMAT_FLOAT64`

:data:`FORMAT_INVALID`

:data:`FORMAT_S16`

:data:`FORMAT_S24`

:data:`FORMAT_S32`

:data:`FORMAT_U8`

:data:`RATE_11025`

:data:`RATE_16000`

:data:`RATE_192000`

:data:`RATE_22050`

:data:`RATE_32000`

:data:`RATE_44100`

:data:`RATE_48000`

:data:`RATE_8000`

:data:`RATE_88200`

:data:`RATE_96000`

:data:`RATE_INVALID`

:data:`STATUS_INVALID`

:data:`STATUS_PAUSED`

:data:`STATUS_PLAYING`

:data:`STATUS_STOPPED`

:class:`aud.AnimateableProperty`

:class:`aud.Device`

:class:`aud.DynamicMusic`

:class:`aud.HRTF`

:class:`aud.Handle`

:class:`aud.ImpulseResponse`

:class:`aud.PlaybackManager`

:class:`aud.Sequence`

:class:`aud.SequenceEntry`

:class:`aud.Sound`

:class:`aud.Source`

:class:`aud.ThreadPool`

:class:`aud.error`

"""

import typing

import numpy

AP_LOCATION: typing.Any = ...

"""

Constant value 3

"""

AP_ORIENTATION: typing.Any = ...

"""

Constant value 4

"""

AP_PANNING: typing.Any = ...

"""

Constant value 1

"""

AP_PITCH: typing.Any = ...

"""

Constant value 2

"""

AP_PITCH_SCALE: typing.Any = ...

"""

Constant value 6

"""

AP_TIME_STRETCH: typing.Any = ...

"""

Constant value 5

"""

AP_VOLUME: typing.Any = ...

"""

Constant value 0

"""

CHANNELS_INVALID: typing.Any = ...

"""

Constant value 0

"""

CHANNELS_MONO: typing.Any = ...

"""

Constant value 1

"""

CHANNELS_STEREO: typing.Any = ...

"""

Constant value 2

"""

CHANNELS_STEREO_LFE: typing.Any = ...

"""

Constant value 3

"""

CHANNELS_SURROUND4: typing.Any = ...

"""

Constant value 4

"""

CHANNELS_SURROUND5: typing.Any = ...

"""

Constant value 5

"""

CHANNELS_SURROUND51: typing.Any = ...

"""

Constant value 6

"""

CHANNELS_SURROUND61: typing.Any = ...

"""

Constant value 7

"""

CHANNELS_SURROUND71: typing.Any = ...

"""

Constant value 8

"""

CODEC_AAC: typing.Any = ...

"""

Constant value 1

"""

CODEC_AC3: typing.Any = ...

"""

Constant value 2

"""

CODEC_FLAC: typing.Any = ...

"""

Constant value 3

"""

CODEC_INVALID: typing.Any = ...

"""

Constant value 0

"""

CODEC_MP2: typing.Any = ...

"""

Constant value 4

"""

CODEC_MP3: typing.Any = ...

"""

Constant value 5

"""

CODEC_OPUS: typing.Any = ...

"""

Constant value 8

"""

CODEC_PCM: typing.Any = ...

"""

Constant value 6

"""

CODEC_VORBIS: typing.Any = ...

"""

Constant value 7

"""

CONTAINER_AAC: typing.Any = ...

"""

Constant value 8

"""

CONTAINER_AC3: typing.Any = ...

"""

Constant value 1

"""

CONTAINER_FLAC: typing.Any = ...

"""

Constant value 2

"""

CONTAINER_INVALID: typing.Any = ...

"""

Constant value 0

"""

CONTAINER_MATROSKA: typing.Any = ...

"""

Constant value 3

"""

CONTAINER_MP2: typing.Any = ...

"""

Constant value 4

"""

CONTAINER_MP3: typing.Any = ...

"""

Constant value 5

"""

CONTAINER_OGG: typing.Any = ...

"""

Constant value 6

"""

CONTAINER_WAV: typing.Any = ...

"""

Constant value 7

"""

DISTANCE_MODEL_EXPONENT: typing.Any = ...

"""

Constant value 5

"""

DISTANCE_MODEL_EXPONENT_CLAMPED: typing.Any = ...

"""

Constant value 6

"""

DISTANCE_MODEL_INVALID: typing.Any = ...

"""

Constant value 0

"""

DISTANCE_MODEL_INVERSE: typing.Any = ...

"""

Constant value 1

"""

DISTANCE_MODEL_INVERSE_CLAMPED: typing.Any = ...

"""

Constant value 2

"""

DISTANCE_MODEL_LINEAR: typing.Any = ...

"""

Constant value 3

"""

DISTANCE_MODEL_LINEAR_CLAMPED: typing.Any = ...

"""

Constant value 4

"""

FORMAT_FLOAT32: typing.Any = ...

"""

Constant value 36

"""

FORMAT_FLOAT64: typing.Any = ...

"""

Constant value 40

"""

FORMAT_INVALID: typing.Any = ...

"""

Constant value 0

"""

FORMAT_S16: typing.Any = ...

"""

Constant value 18

"""

FORMAT_S24: typing.Any = ...

"""

Constant value 19

"""

FORMAT_S32: typing.Any = ...

"""

Constant value 20

"""

FORMAT_U8: typing.Any = ...

"""

Constant value 1

"""

RATE_11025: typing.Any = ...

"""

Constant value 11025

"""

RATE_16000: typing.Any = ...

"""

Constant value 16000

"""

RATE_192000: typing.Any = ...

"""

Constant value 192000

"""

RATE_22050: typing.Any = ...

"""

Constant value 22050

"""

RATE_32000: typing.Any = ...

"""

Constant value 32000

"""

RATE_44100: typing.Any = ...

"""

Constant value 44100

"""

RATE_48000: typing.Any = ...

"""

Constant value 48000

"""

RATE_8000: typing.Any = ...

"""

Constant value 8000

"""

RATE_88200: typing.Any = ...

"""

Constant value 88200

"""

RATE_96000: typing.Any = ...

"""

Constant value 96000

"""

RATE_INVALID: typing.Any = ...

"""

Constant value 0

"""

STATUS_INVALID: typing.Any = ...

"""

Constant value 0

"""

STATUS_PAUSED: typing.Any = ...

"""

Constant value 2

"""

STATUS_PLAYING: typing.Any = ...

"""

Constant value 1

"""

STATUS_STOPPED: typing.Any = ...

"""

Constant value 3

"""

class aud.AnimateableProperty:

  """

  An AnimateableProperty object stores an array of float values for animating sound properties (e.g. pan, volume, pitch-scale)

  """

  def read(self, position: float) -> numpy.ndarray:

    """

    Reads the properties value at the given position.

    """

    ...

  def readSingle(self, position: float) -> float:

    """

    Reads the properties value at the given position, assuming there is exactly one value.

    """

    ...

  def write(self, data: typing.Any, position: int = None) -> None:

    """

    Writes the properties value.

    If *position* is also given, the property is marked animated and
the values are written starting at *position*.

    """

    ...

  def writeConstantRange(self, data: typing.Any, position_start: int, position_end: int) -> None:

    """

    Fills the properties frame range with a constant value and marks it animated.

    """

    ...

  animated: typing.Any = ...

  """

  Whether the property is animated.

  """

  count: typing.Any = ...

  """

  The count of floats for a property.

  """

class aud.Device:

  """

  Device objects represent an audio output backend like OpenAL or SDL, but might also represent a file output or RAM buffer output.

  """

  def lock(self) -> None:

    """

    Locks the device so that it's guaranteed, that no samples are
read from the streams until :meth:`unlock` is called.
This is useful if you want to do start/stop/pause/resume some
sounds at the same time.

    Note: The device has to be unlocked as often as locked to be
able to continue playback.

    Warning: Make sure the time between locking and unlocking is
as short as possible to avoid clicks.

    """

    ...

  def play(self, sound: Sound, keep: bool = False) -> Handle:

    """

    Plays a sound.

    """

    ...

  def stopAll(self) -> None:

    """

    Stops all playing and paused sounds.

    """

    ...

  def unlock(self) -> None:

    """

    Unlocks the device after a lock call, see :meth:`lock` for
details.

    """

    ...

  channels: typing.Any = ...

  """

  The channel count of the device.

  """

  distance_model: typing.Any = ...

  """

  The distance model of the device.

  `OpenAL Documentation <https://www.openal.org/documentation/>`_

  """

  doppler_factor: typing.Any = ...

  """

  The doppler factor of the device.
This factor is a scaling factor for the velocity vectors in doppler calculation. So a value bigger than 1 will exaggerate the effect as it raises the velocity.

  """

  format: typing.Any = ...

  """

  The native sample format of the device.

  """

  listener_location: typing.Any = ...

  """

  The listeners's location in 3D space, a 3D tuple of floats.

  """

  listener_orientation: typing.Any = ...

  """

  The listener's orientation in 3D space as quaternion, a 4 float tuple.

  """

  listener_velocity: typing.Any = ...

  """

  The listener's velocity in 3D space, a 3D tuple of floats.

  """

  rate: typing.Any = ...

  """

  The sampling rate of the device in Hz.

  """

  speed_of_sound: typing.Any = ...

  """

  The speed of sound of the device.
The speed of sound in air is typically 343.3 m/s.

  """

  volume: typing.Any = ...

  """

  The overall volume of the device.

  """

class aud.DynamicMusic:

  """

  The DynamicMusic object allows to play music depending on a current scene, scene changes are managed by the class, with the possibility of custom transitions.
The default transition is a crossfade effect, and the default scene is silent and has id 0

  """

  def addScene(self, scene: Sound) -> int:

    """

    Adds a new scene.

    """

    ...

  def addTransition(self, ini: int, end: int, transition: Sound) -> bool:

    """

    Adds a new scene.

    """

    ...

  def pause(self) -> bool:

    """

    Pauses playback of the scene.

    """

    ...

  def resume(self) -> bool:

    """

    Resumes playback of the scene.

    """

    ...

  def stop(self) -> bool:

    """

    Stops playback of the scene.

    """

    ...

  fadeTime: typing.Any = ...

  """

  The length in seconds of the crossfade transition

  """

  position: typing.Any = ...

  """

  The playback position of the scene in seconds.

  """

  scene: typing.Any = ...

  """

  The current scene

  """

  status: typing.Any = ...

  """

  Whether the scene is playing, paused or stopped (=invalid).

  """

  volume: typing.Any = ...

  """

  The volume of the scene.

  """

class aud.HRTF:

  """

  An HRTF object represents a set of head related transfer functions as impulse responses. It's used for binaural sound

  """

  def loadLeftHrtfSet(self, extension: str, directory: typing.Any) -> HRTF:

    """

    Loads all HRTFs from a directory.

    """

    ...

  def loadRightHrtfSet(self, extension: str, directory: typing.Any) -> HRTF:

    """

    Loads all HRTFs from a directory.

    """

    ...

  def addImpulseResponseFromSound(self, sound: Sound, azimuth: float, elevation: float) -> bool:

    """

    Adds a new hrtf to the HRTF object

    """

    ...

class aud.Handle:

  """

  Handle objects are playback handles that can be used to control playback of a sound. If a sound is played back multiple times then there are as many handles.

  """

  def pause(self) -> bool:

    """

    Pauses playback.

    """

    ...

  def resume(self) -> bool:

    """

    Resumes playback.

    """

    ...

  def stop(self) -> bool:

    """

    Stops playback.

    Note: This makes the handle invalid.

    """

    ...

  attenuation: typing.Any = ...

  """

  This factor is used for distance based attenuation of the source.

  :attr:`Device.distance_model`

  """

  cone_angle_inner: typing.Any = ...

  """

  The opening angle of the inner cone of the source. If the cone values of a source are set there are two (audible) cones with the apex at the :attr:`location` of the source and with infinite height, heading in the direction of the source's :attr:`orientation`.
In the inner cone the volume is normal. Outside the outer cone the volume will be :attr:`cone_volume_outer` and in the area between the volume will be interpolated linearly.

  """

  cone_angle_outer: typing.Any = ...

  """

  The opening angle of the outer cone of the source.

  :attr:`cone_angle_inner`

  """

  cone_volume_outer: typing.Any = ...

  """

  The volume outside the outer cone of the source.

  :attr:`cone_angle_inner`

  """

  distance_maximum: typing.Any = ...

  """

  The maximum distance of the source.
If the listener is further away the source volume will be 0.

  :attr:`Device.distance_model`

  """

  distance_reference: typing.Any = ...

  """

  The reference distance of the source.
At this distance the volume will be exactly :attr:`volume`.

  :attr:`Device.distance_model`

  """

  keep: typing.Any = ...

  """

  Whether the sound should be kept paused in the device when its end is reached.
This can be used to seek the sound to some position and start playback again.

  Warning: If this is set to true and you forget stopping this equals a memory leak as the handle exists until the device is destroyed.

  """

  location: typing.Any = ...

  """

  The source's location in 3D space, a 3D tuple of floats.

  """

  loop_count: typing.Any = ...

  """

  The (remaining) loop count of the sound. A negative value indicates infinity.

  """

  orientation: typing.Any = ...

  """

  The source's orientation in 3D space as quaternion, a 4 float tuple.

  """

  pitch: typing.Any = ...

  """

  The pitch of the sound.

  """

  position: typing.Any = ...

  """

  The playback position of the sound in seconds.

  """

  relative: typing.Any = ...

  """

  Whether the source's location, velocity and orientation is relative or absolute to the listener.

  """

  status: typing.Any = ...

  """

  Whether the sound is playing, paused or stopped (=invalid).

  """

  velocity: typing.Any = ...

  """

  The source's velocity in 3D space, a 3D tuple of floats.

  """

  volume: typing.Any = ...

  """

  The volume of the sound.

  """

  volume_maximum: typing.Any = ...

  """

  The maximum volume of the source.

  :attr:`Device.distance_model`

  """

  volume_minimum: typing.Any = ...

  """

  The minimum volume of the source.

  :attr:`Device.distance_model`

  """

class aud.ImpulseResponse:

  """

  An ImpulseResponse object represents a filter with which to convolve a sound.

  """

  ...

class aud.PlaybackManager:

  """

  A PlabackManager object allows to easily control groups os sounds organized in categories.

  """

  def addCategory(self, volume: float) -> int:

    """

    Adds a category with a custom volume.

    """

    ...

  def clean(self) -> None:

    """

    Cleans all the invalid and finished sound from the playback manager.

    """

    ...

  def getVolume(self, catKey: int) -> float:

    """

    Retrieves the volume of a category.

    """

    ...

  def pause(self, catKey: int) -> bool:

    """

    Pauses playback of the category.

    """

    ...

  def play(self, sound: Sound, catKey: int) -> Handle:

    """

    Plays a sound through the playback manager and assigns it to a category.

    """

    ...

  def resume(self, catKey: int) -> bool:

    """

    Resumes playback of the catgory.

    """

    ...

  def setVolume(self, volume: float, catKey: int) -> int:

    """

    Changes the volume of a category.

    """

    ...

  def stop(self, catKey: int) -> bool:

    """

    Stops playback of the category.

    """

    ...

class aud.Sequence:

  """

  This sound represents sequenced entries to play a sound sequence.

  """

  def add(self) -> SequenceEntry:

    """

    Adds a new entry to the sequence.

    """

    ...

  def remove(self) -> None:

    """

    Removes an entry from the sequence.

    """

    ...

  def setAnimationData(self) -> None:

    """

    Writes animation data to a sequence.

    """

    ...

  channels: typing.Any = ...

  """

  The channel count of the sequence.

  """

  distance_model: typing.Any = ...

  """

  The distance model of the sequence.

  `OpenAL Documentation <https://www.openal.org/documentation/>`_

  """

  doppler_factor: typing.Any = ...

  """

  The doppler factor of the sequence.
This factor is a scaling factor for the velocity vectors in doppler calculation. So a value bigger than 1 will exaggerate the effect as it raises the velocity.

  """

  fps: typing.Any = ...

  """

  The listeners's location in 3D space, a 3D tuple of floats.

  """

  muted: typing.Any = ...

  """

  Whether the whole sequence is muted.

  """

  rate: typing.Any = ...

  """

  The sampling rate of the sequence in Hz.

  """

  speed_of_sound: typing.Any = ...

  """

  The speed of sound of the sequence.
The speed of sound in air is typically 343.3 m/s.

  """

class aud.SequenceEntry:

  """

  SequenceEntry objects represent an entry of a sequenced sound.

  """

  def move(self) -> None:

    """

    Moves the entry.

    """

    ...

  def setAnimationData(self) -> None:

    """

    Writes animation data to a sequenced entry.

    """

    ...

  attenuation: typing.Any = ...

  """

  This factor is used for distance based attenuation of the source.

  :attr:`Device.distance_model`

  """

  cone_angle_inner: typing.Any = ...

  """

  The opening angle of the inner cone of the source. If the cone values of a source are set there are two (audible) cones with the apex at the :attr:`location` of the source and with infinite height, heading in the direction of the source's :attr:`orientation`.
In the inner cone the volume is normal. Outside the outer cone the volume will be :attr:`cone_volume_outer` and in the area between the volume will be interpolated linearly.

  """

  cone_angle_outer: typing.Any = ...

  """

  The opening angle of the outer cone of the source.

  :attr:`cone_angle_inner`

  """

  cone_volume_outer: typing.Any = ...

  """

  The volume outside the outer cone of the source.

  :attr:`cone_angle_inner`

  """

  distance_maximum: typing.Any = ...

  """

  The maximum distance of the source.
If the listener is further away the source volume will be 0.

  :attr:`Device.distance_model`

  """

  distance_reference: typing.Any = ...

  """

  The reference distance of the source.
At this distance the volume will be exactly :attr:`volume`.

  :attr:`Device.distance_model`

  """

  muted: typing.Any = ...

  """

  Whether the entry is muted.

  """

  relative: typing.Any = ...

  """

  Whether the source's location, velocity and orientation is relative or absolute to the listener.

  """

  sound: typing.Any = ...

  """

  The sound the entry is representing and will be played in the sequence.

  """

  volume_maximum: typing.Any = ...

  """

  The maximum volume of the source.

  :attr:`Device.distance_model`

  """

  volume_minimum: typing.Any = ...

  """

  The minimum volume of the source.

  :attr:`Device.distance_model`

  """

class aud.Sound:

  """

  Sound objects are immutable and represent a sound that can be played simultaneously multiple times. They are called factories because they create reader objects internally that are used for playback.

  """

  @classmethod

  def buffer(cls, data: numpy.ndarray, rate: float) -> Sound:

    """

    Creates a sound from a data buffer.

    """

    ...

  @classmethod

  def file(cls, filename: str) -> Sound:

    """

    Creates a sound object of a sound file.

    Warning: If the file doesn't exist or can't be read you will
not get an exception immediately, but when you try to start
playback of that sound.

    """

    ...

  @classmethod

  def list(cls) -> Sound:

    """

    Creates an empty sound list that can contain several sounds.

    """

    ...

  @classmethod

  def sawtooth(cls, frequency: float, rate: int = 48000) -> Sound:

    """

    Creates a sawtooth sound which plays a sawtooth wave.

    """

    ...

  @classmethod

  def silence(cls, rate: int = 48000) -> Sound:

    """

    Creates a silence sound which plays simple silence.

    """

    ...

  @classmethod

  def sine(cls, frequency: float, rate: int = 48000) -> Sound:

    """

    Creates a sine sound which plays a sine wave.

    """

    ...

  @classmethod

  def square(cls, frequency: float, rate: int = 48000) -> Sound:

    """

    Creates a square sound which plays a square wave.

    """

    ...

  @classmethod

  def triangle(cls, frequency: float, rate: int = 48000) -> Sound:

    """

    Creates a triangle sound which plays a triangle wave.

    """

    ...

  def ADSR(self, attack: float, decay: float, sustain: float, release: float) -> Sound:

    """

    Attack-Decay-Sustain-Release envelopes the volume of a sound.
Note: there is currently no way to trigger the release with this API.

    """

    ...

  def accumulate(self, additive: typing.Any = False) -> Sound:

    """

    Accumulates a sound by summing over positive input
differences thus generating a monotonic sigal.
If additivity is set to true negative input differences get added too,
but positive ones with a factor of two.

    Note that with additivity the signal is not monotonic anymore.

    """

    ...

  def addSound(self, sound: Sound) -> None:

    """

    Adds a new sound to a sound list.

    Note: You can only add a sound to a sound list.

    """

    ...

  def binaural(self) -> Sound:

    """

    Creates a binaural sound using another sound as source. The original sound must be mono

    """

    ...

  def cache(self) -> Sound:

    """

    Caches a sound into RAM.

    This saves CPU usage needed for decoding and file access if the
underlying sound reads from a file on the harddisk,
but it consumes a lot of memory.

    Note: Only known-length factories can be buffered.

    Warning: Raw PCM data needs a lot of space, only buffer
short factories.

    """

    ...

  def convolver(self) -> Sound:

    """

    Creates a sound that will apply convolution to another sound.

    """

    ...

  def data(self) -> numpy.ndarray:

    """

    Retrieves the data of the sound as numpy array.

    Note: Best efficiency with cached sounds.

    """

    ...

  def delay(self, time: float) -> Sound:

    """

    Delays by playing adding silence in front of the other sound's data.

    """

    ...

  def envelope(self, attack: float, release: float, threshold: float, arthreshold: float) -> Sound:

    """

    Delays by playing adding silence in front of the other sound's data.

    """

    ...

  def fadein(self, start: float, length: float) -> Sound:

    """

    Fades a sound in by raising the volume linearly in the given
time interval.

    Note: Before the fade starts it plays silence.

    """

    ...

  def fadeout(self, start: float, length: float) -> Sound:

    """

    Fades a sound in by lowering the volume linearly in the given
time interval.

    Note: After the fade this sound plays silence, so that
the length of the sound is not altered.

    """

    ...

  def filter(self, b: typing.Sequence[float], a: typing.Sequence[float] = (1,)) -> Sound:

    """

    Filters a sound with the supplied IIR filter coefficients.
Without the second parameter you'll get a FIR filter.

    If the first value of the a sequence is 0,
it will be set to 1 automatically.
If the first value of the a sequence is neither 0 nor 1, all
filter coefficients will be scaled by this value so that it is 1
in the end, you don't have to scale yourself.

    """

    ...

  def highpass(self, frequency: float, Q: float = 0.5) -> Sound:

    """

    Creates a second order highpass filter based on the transfer
function H(s) = s^2 / (s^2 + s/Q + 1)

    """

    ...

  def join(self, sound: Sound) -> Sound:

    """

    Plays two factories in sequence.

    Note: The two factories have to have the same specifications
(channels and samplerate).

    """

    ...

  def limit(self, start: float, end: float) -> Sound:

    """

    Limits a sound within a specific start and end time.

    """

    ...

  def loop(self, count: int) -> Sound:

    """

    Loops a sound.

    Note: This is a filter function, you might consider using
:attr:`Handle.loop_count` instead.

    """

    ...

  def lowpass(self, frequency: float, Q: float = 0.5) -> Sound:

    """

    Creates a second order lowpass filter based on the transfer    function H(s) = 1 / (s^2 + s/Q + 1)

    """

    ...

  def mix(self, sound: Sound) -> Sound:

    """

    Mixes two factories.

    Note: The two factories have to have the same specifications
(channels and samplerate).

    """

    ...

  def modulate(self, sound: Sound) -> Sound:

    """

    Modulates two factories.

    Note: The two factories have to have the same specifications
(channels and samplerate).

    """

    ...

  def mutable(self) -> Sound:

    """

    Creates a sound that will be restarted when sought backwards.
If the original sound is a sound list, the playing sound can change.

    """

    ...

  def pingpong(self) -> Sound:

    """

    Plays a sound forward and then backward.
This is like joining a sound with its reverse.

    """

    ...

  def pitch(self, factor: float) -> Sound:

    """

    Changes the pitch of a sound with a specific factor.

    Note: This is done by changing the sample rate of the
underlying sound, which has to be an integer, so the factor
value rounded and the factor may not be 100 % accurate.

    Note: This is a filter function, you might consider using
:attr:`Handle.pitch` instead.

    """

    ...

  def rechannel(self, channels: int) -> Sound:

    """

    Rechannels the sound.

    """

    ...

  def resample(self, rate: float, quality: int) -> Sound:

    """

    Resamples the sound.

    """

    ...

  def reverse(self) -> Sound:

    """

    Plays a sound reversed.

    Note: The sound has to have a finite length and has to be seekable.
It's recommended to use this only with factories with
fast and accurate seeking, which is not true for encoded audio
files, such ones should be buffered using :meth:`cache` before
being played reversed.

    Warning: If seeking is not accurate in the underlying sound
you'll likely hear skips/jumps/cracks.

    """

    ...

  def sum(self) -> Sound:

    """

    Sums the samples of a sound.

    """

    ...

  def threshold(self, threshold: float = 0) -> Sound:

    """

    Makes a threshold wave out of an audio wave by setting all samples
with a amplitude >= threshold to 1, all <= -threshold to -1 and
all between to 0.

    """

    ...

  def volume(self, volume: float) -> Sound:

    """

    Changes the volume of a sound.

    Note: Should be in the range [0, 1] to avoid clipping.

    Note: This is a filter function, you might consider using
:attr:`Handle.volume` instead.

    """

    ...

  def write(self, filename: str, rate: int, channels: int, format: int, container: int, codec: int, bitrate: int, buffersize: int) -> None:

    """

    Writes the sound to a file.

    """

    ...

  length: typing.Any = ...

  """

  The sample specification of the sound as a tuple with rate and channel count.

  """

  specs: typing.Any = ...

  """

  The sample specification of the sound as a tuple with rate and channel count.

  """

class aud.Source:

  """

  The source object represents the source position of a binaural sound.

  """

  azimuth: typing.Any = ...

  """

  The azimuth angle.

  """

  distance: typing.Any = ...

  """

  The distance value. 0 is min, 1 is max.

  """

  elevation: typing.Any = ...

  """

  The elevation angle.

  """

class aud.ThreadPool:

  """

  A ThreadPool is used to parallelize convolution efficiently.

  """

  ...

class aud.error:

  ...
