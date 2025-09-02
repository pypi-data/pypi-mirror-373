"""Color helpers"""

from typing import TypeAlias, cast

Color: TypeAlias = tuple[int, int, int, int]


def convert_to_rgba(hex_color: str) -> Color:
  """
  Convert Hex (or Hexa) color to RGB (or RGBA) color

  :param hex_color: Hex color
  :type hex_color: str

  :return: RGB or RGBA color
  :rtype: tuple

  :raises ValueError: If the color is invalid
  """

  if not hex_color.startswith('#'):
    raise ValueError('Invalid color, must starts with #')

  hex_color = hex_color.replace('#', '')
  if len(hex_color) == 6:
    return cast(Color, tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (1,))

  return cast(Color, tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4, 6)))


def use_black(color: str) -> bool:
  """
  Use black
  Will return when the background color works well with black text color.
  Note: This method is not 100% accurate and will not work with alpha channel (Hexa color)
  :param color: Hex color
  :type color: str
  :return: True if the color works well with black text color
  :rtype: bool
  :raises ValueError: If the color is invalid
  """
  rgb = convert_to_rgba(color)
  a = 1 - (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
  return a < 0.5
