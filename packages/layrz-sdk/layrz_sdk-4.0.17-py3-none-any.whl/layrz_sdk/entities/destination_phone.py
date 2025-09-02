from typing import Self

from pydantic import BaseModel, Field


class DestinationPhone(BaseModel):
  """Destination Phone"""

  phone_number: str = Field(
    ...,
    description='Defines the phone number for Twilio notifications',
    alias='phoneNumber',
  )

  country_code: str = Field(
    ...,
    description='Defines the country code for the phone number',
    alias='countryCode',
  )

  @property
  def formatted_phone_number(self: Self) -> str:
    """Returns the formatted phone number"""
    return f'{self.country_code}{self.phone_number}'
