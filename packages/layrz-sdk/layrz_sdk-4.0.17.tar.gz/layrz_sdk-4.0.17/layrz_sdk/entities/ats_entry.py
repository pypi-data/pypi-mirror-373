"""Entry entity"""

from pydantic import BaseModel, Field


class AtsEntry(BaseModel):
  """Entry entity"""

  pk: int = Field(description='Defines the primary key of the Function', alias='id')
  old_tank_level: float = Field(description='Old tank level in liters', default=0.0)
  new_tank_level: float = Field(description='New tank level in liters', default=0.0)
  density: float | None = Field(description='Density of the fuel in kg/m3', default=None)
  temperature: float | None = Field(description='Temperature of the fuel in Celsius', default=None)
  is_executed_by_command: bool = Field(description='Indicates if the entry is executed by command', default=False)
