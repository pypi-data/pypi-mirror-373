"""Asset contact information"""

from pydantic import BaseModel, Field


class AssetContact(BaseModel):
  """Asset contact information"""

  name: str = Field(default='', description='Name of the contact person for the asset')
  phone: str = Field(default='', description='Phone number of the contact person for the asset')
  email: str = Field(default='', description='Email address of the contact person for the asset')
