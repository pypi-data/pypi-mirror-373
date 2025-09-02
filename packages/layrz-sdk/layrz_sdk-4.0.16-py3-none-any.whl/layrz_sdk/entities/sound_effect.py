"""SoundEffect"""

from enum import StrEnum
from typing import Self


class SoundEffect(StrEnum):
  """
  SoundEffect definition
  """

  NONE = 'NONE'
  """ No sound """

  BEEP = 'BEEP'
  """ A short, sharp electronic sound, often associated with alerts or signals. """

  MECHANICAL = 'MECHANICAL'
  """ A sound resembling a machine or device, characterized by clicking, whirring, or other industrial tones. """

  PEAL = 'PEAL'
  """ A clear, ringing sound, reminiscent of a bell or a chime. """

  POP = 'POP'
  """ A quick, soft burst-like sound, similar to a bubble popping. """

  RESONANT = 'RESONANT'
  """ A deep, echoing tone with a lasting vibration or reverberation. """

  TONE = 'TONE'
  """ A steady, smooth sound with a consistent pitch, often used in signals or melodies. """

  CUSTOM = 'CUSTOM'
  """ A custom sound effect that can be set by the user. """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'SoundEffect.{self.name}'
