import json
from datetime import datetime
from typing import Any

import pytest

from layrz_sdk.constants import UTC
from layrz_sdk.lcl.core import LclCore

"""Test LCL functions"""


def _process_and_convert(lcl: LclCore) -> Any:
  result = lcl.perform()
  try:
    result = json.loads(result)
  except json.JSONDecodeError:
    pass

  return result


def test_get_param() -> None:
  formula = 'GET_PARAM("test.param", None)'
  lcl = LclCore(script=formula, payload={'test.param': 10})
  result = _process_and_convert(lcl)
  assert result == 10.0

  lcl = LclCore(script=formula, payload={})
  result = _process_and_convert(lcl)
  assert result is None


def test_get_sensor() -> None:
  formula = 'GET_SENSOR("test.sensor", None)'
  lcl = LclCore(script=formula, sensors={'test.sensor': 10})
  result = _process_and_convert(lcl)
  assert result == 10.0

  lcl = LclCore(script=formula, sensors={})
  result = _process_and_convert(lcl)
  assert result is None


def test_constant() -> None:
  formula = 'CONSTANT(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  lcl = LclCore(script='CONSTANT(False)')
  result = _process_and_convert(lcl)
  assert not result

  lcl = LclCore(script='CONSTANT(None)')
  result = _process_and_convert(lcl)
  assert result is None

  lcl = LclCore(script='CONSTANT(10)')
  result = _process_and_convert(lcl)
  assert result == 10.0


def test_get_custom_field() -> None:
  formula = 'GET_CUSTOM_FIELD("test.custom_field")'
  lcl = LclCore(script=formula, custom_fields={'test.custom_field': 10})
  result = _process_and_convert(lcl)
  assert result == 10.0

  lcl = LclCore(script=formula, custom_fields={})
  result = _process_and_convert(lcl)
  assert result == ''


def test_compare() -> None:
  formula = 'COMPARE(CONSTANT(10), CONSTANT(10))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'COMPARE(CONSTANT(10), None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'COMPARE(CONSTANT(10), None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'COMPARE(CONSTANT(10), CONSTANT(20))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result


def test_or_operator() -> None:
  formula = 'OR_OPERATOR(CONSTANT(True), CONSTANT(False))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'OR_OPERATOR(CONSTANT(False), CONSTANT(False))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'OR_OPERATOR(CONSTANT(True), CONSTANT(True))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'OR_OPERATOR(CONSTANT(False), CONSTANT(None))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_and_operator() -> None:
  formula = 'AND_OPERATOR(CONSTANT(True), CONSTANT(False))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'AND_OPERATOR(CONSTANT(False), CONSTANT(False))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'AND_OPERATOR(CONSTANT(True), CONSTANT(True))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'AND_OPERATOR(CONSTANT(False), CONSTANT(None))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_sum() -> None:
  formula = 'SUM(CONSTANT(10), CONSTANT(20))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 30.0

  formula = 'SUM(CONSTANT(10), None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_substract() -> None:
  formula = 'SUBSTRACT(CONSTANT(10), CONSTANT(20))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == -10.0

  formula = 'SUBSTRACT(CONSTANT(20), CONSTANT(10))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 10.0

  formula = 'SUBSTRACT(CONSTANT(10), None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_multiply() -> None:
  formula = 'MULTIPLY(CONSTANT(10), CONSTANT(20))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 200.0

  formula = 'MULTIPLY(CONSTANT(20), CONSTANT(10))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 200.0

  formula = 'MULTIPLY(CONSTANT(10), None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_divide() -> None:
  formula = 'DIVIDE(CONSTANT(10), CONSTANT(20))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 0.5

  formula = 'DIVIDE(CONSTANT(20), CONSTANT(10))'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 2.0

  formula = 'DIVIDE(CONSTANT(10), None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_to_bool() -> None:
  formula = 'TO_BOOL(1)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'TO_BOOL(0)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'TO_BOOL(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'TO_BOOL("True")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'TO_BOOL("False")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result


def test_to_str() -> None:
  formula = 'TO_STR(1)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == '1'

  formula = 'TO_STR(1.1)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == '1.1'

  formula = 'TO_STR(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'True'

  formula = 'TO_STR(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_to_int() -> None:
  formula = 'TO_INT(1.5)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'TO_INT("1")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'TO_INT(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'TO_INT(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_ceil() -> None:
  formula = 'CEIL(1.2)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 2

  formula = 'CEIL(1.5)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 2

  formula = 'CEIL("hola")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid arguments - must be real number, not str'

  formula = 'CEIL(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'CEIL(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_floor() -> None:
  formula = 'FLOOR(1.2)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'FLOOR(1.5)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'FLOOR("hola")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid arguments - must be real number, not str'

  formula = 'FLOOR(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'FLOOR(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_round() -> None:
  formula = 'ROUND(1.2)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'ROUND(1.5)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 2

  formula = 'ROUND("hola")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid arguments - must be real number, not str'

  formula = 'ROUND(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'ROUND(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_sqrt() -> None:
  formula = 'SQRT(4)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 2

  formula = 'SQRT(9)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 3

  formula = 'SQRT("hola")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid arguments - must be real number, not str'

  formula = 'SQRT(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'SQRT(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_concat() -> None:
  formula = 'CONCAT("Hello", " ", "World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Hello World'

  formula = 'CONCAT("Hello", None, "World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'CONCAT("Hello", 10, "World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Hello10World'

  formula = 'CONCAT("Hello", True, "World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'HelloTrueWorld'


def test_now() -> None:
  formula = 'NOW()'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert isinstance(result, (int, float))


def test_random() -> None:
  formula = 'RANDOM(0, 1)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert isinstance(result, float)

  assert 0.0 <= result <= 1.0


def test_random_int() -> None:
  formula = 'RANDOM_INT(1, 3)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert isinstance(result, int)
  assert 1 <= result <= 3


def test_greater_than_or_equals_to() -> None:
  formula = 'GREATER_THAN_OR_EQUALS_TO(10, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'GREATER_THAN_OR_EQUALS_TO(10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'GREATER_THAN_OR_EQUALS_TO(20, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'GREATER_THAN_OR_EQUALS_TO(10, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'GREATER_THAN_OR_EQUALS_TO(None, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_greater_than() -> None:
  formula = 'GREATER_THAN(10, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'GREATER_THAN(10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'GREATER_THAN(20, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'GREATER_THAN(10, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'GREATER_THAN(None, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_less_than_or_equals_to() -> None:
  formula = 'LESS_THAN_OR_EQUALS_TO(10, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'LESS_THAN_OR_EQUALS_TO(10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'LESS_THAN_OR_EQUALS_TO(20, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'LESS_THAN_OR_EQUALS_TO(10, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'LESS_THAN_OR_EQUALS_TO(None, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_less_than() -> None:
  formula = 'LESS_THAN(10, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'LESS_THAN(10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'LESS_THAN(20, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'LESS_THAN(10, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'LESS_THAN(None, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_different() -> None:
  formula = 'DIFFERENT(10, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'DIFFERENT(10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'DIFFERENT(20, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'DIFFERENT(10, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'DIFFERENT(None, 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'DIFFERENT("Hola", 10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid data types - arg1: str - arg2: float'


def test_hex_to_str() -> None:
  formula = 'HEX_TO_STR("48656c6c6f")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Hello'

  formula = 'HEX_TO_STR("0x48656c6c6f")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Hello'

  formula = 'HEX_TO_STR("1")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid hex string'


def test_str_to_hex() -> None:
  formula = 'STR_TO_HEX("Hello")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == '48656c6c6f'


def test_hex_to_int() -> None:
  formula = 'HEX_TO_INT("0xff")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 255

  formula = 'HEX_TO_INT("0x1")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1

  formula = 'HEX_TO_INT("Helo")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid hex string'


def test_int_to_hex() -> None:
  formula = 'INT_TO_HEX(15)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'f'

  formula = 'INT_TO_HEX(1)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == '1'

  formula = 'INT_TO_HEX("Hello")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid int value'


def test_to_float() -> None:
  formula = 'TO_FLOAT(0)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 0.0

  formula = 'TO_FLOAT(1)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1.0

  formula = 'TO_FLOAT(1.1)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 1.1

  formula = 'TO_FLOAT("Hello")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Invalid arguments - must be real number, not str'


def test_get_distance_traveled() -> None:
  formula = 'GET_DISTANCE_TRAVELED()'
  lcl = LclCore(script=formula, asset_constants={'distanceTraveled': 10})
  result = _process_and_convert(lcl)
  assert result == 10.0

  lcl = LclCore(script=formula, asset_constants={})
  result = _process_and_convert(lcl)
  assert result == 0.0


def test_get_previous_sensor() -> None:
  formula = 'GET_PREVIOUS_SENSOR("test.sensor")'
  lcl = LclCore(script=formula, previous_sensors={'test.sensor': 10})
  result = _process_and_convert(lcl)
  assert result == 10.0

  lcl = LclCore(script=formula, previous_sensors={})
  result = _process_and_convert(lcl)
  assert result is None


def test_is_parameter_present() -> None:
  formula = 'IS_PARAMETER_PRESENT("test.param")'
  lcl = LclCore(script=formula, payload={'test.param': 10})
  result = _process_and_convert(lcl)
  assert result

  lcl = LclCore(script=formula, payload={})
  result = _process_and_convert(lcl)
  assert not result


def test_is_sensor_present() -> None:
  formula = 'IS_SENSOR_PRESENT("test.sensor")'
  lcl = LclCore(script=formula, sensors={'test.sensor': 10})
  result = _process_and_convert(lcl)
  assert result

  lcl = LclCore(script=formula, sensors={})
  result = _process_and_convert(lcl)
  assert not result


def test_inside_range() -> None:
  formula = 'INSIDE_RANGE(10, 20, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'INSIDE_RANGE(10, 5, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'INSIDE_RANGE(10, 5, 15)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'INSIDE_RANGE(None, 15, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'INSIDE_RANGE(10, None, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'INSIDE_RANGE(10, 15, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_outside_range() -> None:
  formula = 'OUTSIDE_RANGE(10, 20, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'OUTSIDE_RANGE(10, 5, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'OUTSIDE_RANGE(10, 5, 15)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'OUTSIDE_RANGE(None, 15, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'OUTSIDE_RANGE(10, None, 30)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'OUTSIDE_RANGE(10, 15, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_get_time_difference() -> None:
  formula = 'GET_TIME_DIFFERENCE()'
  lcl = LclCore(script=formula, asset_constants={'timeElapsed': 10})
  result = _process_and_convert(lcl)
  assert result == 10

  lcl = LclCore(script=formula, asset_constants={})
  result = _process_and_convert(lcl)
  assert result == 0


def test_if() -> None:
  formula = 'IF(True, 10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 10.0

  formula = 'IF(False, 10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 20.0

  formula = 'IF(None, 10, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'IF(True, None, 20)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'IF(False, 10, None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_regex() -> None:
  formula = 'REGEX("1. Hello world", "^[0-9]+\\.\\s")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'REGEX("1. Hello world", "^[0-9]+\\s")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'REGEX("Hello world", "^[0-9]+\\s")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'REGEX("Hello world", None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'REGEX(None, "^[0-9]+\\s")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_is_none() -> None:
  formula = 'IS_NONE(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'IS_NONE(10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result


def test_not() -> None:
  formula = 'NOT(True)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'NOT(False)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'NOT(None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None

  formula = 'NOT(10)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result


def test_contains() -> None:
  formula = 'CONTAINS("Hello", "Hello World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'CONTAINS("World", "Hello World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'CONTAINS("Hello World", 15)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'CONTAINS("Hello World", None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_starts_with() -> None:
  formula = 'STARTS_WITH("Hello", "Hello World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'STARTS_WITH("World", "Hello World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'STARTS_WITH("Hello World", 15)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'STARTS_WITH("Hello World", None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_ends_with() -> None:
  formula = 'ENDS_WITH("World", "Hello World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result

  formula = 'ENDS_WITH("Hello", "Hello World")'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'ENDS_WITH("Hello World", 15)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert not result

  formula = 'ENDS_WITH("Hello World", None)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result is None


def test_primary_device() -> None:
  formula = 'PRIMARY_DEVICE()'
  lcl = LclCore(script=formula, asset_constants={'primaryDevice': 'test'})
  result = _process_and_convert(lcl)
  assert result == 'test'

  formula = 'PRIMARY_DEVICE()'
  lcl = LclCore(script=formula, asset_constants={})
  result = _process_and_convert(lcl)
  assert result is None


def test_substring() -> None:
  formula = 'SUBSTRING("Hello World", 0, 5)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'Hello'

  formula = 'SUBSTRING("Hello World", 6)'
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == 'World'


def test_unix_to_str() -> None:
  formula = 'UNIX_TO_STR(NOW(), "%Y_%m_%d", "UTC")'
  now = datetime.now(UTC)
  lcl = LclCore(script=formula)
  result = _process_and_convert(lcl)
  assert result == now.strftime('%Y_%m_%d')
