"""Entry entity"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .ats_purchaseorder import AtsPurchaseOrder, DeliveryCategories, OrderCategories, OrderStatus


class AtsOperationMovement(BaseModel):
  """Ats operation movement entity"""

  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
      OrderStatus: lambda v: v.value,
    },
  }
  pk: int = Field(description='Defines the primary key of the Function', alias='id')
  status: OrderStatus = Field(..., description='Current status of the order')
  created_at: datetime = Field(description='Timestamp when the operation movement was created')
  asset_id: int = Field(description='ID of the asset')
  operation_id: int = Field(description='ID of the operation')


class AtsOperation(BaseModel):
  """Entry entity"""

  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
      OrderStatus: lambda v: v.value,
      OrderCategories: lambda v: v.value,
      DeliveryCategories: lambda v: v.value,
    },
  }
  pk: int = Field(description='Defines the primary key of the Function', alias='id')
  purchased_at: datetime = Field(description='Timestamp when the operation was purchased')
  order_status: OrderStatus = Field(..., description='Current status of the order')
  category: OrderCategories = Field(..., description='Category of the operation')
  deliver_category: DeliveryCategories = Field(..., description='Delivery category of the operation')
  seller_asset_id: int = Field(description='ID of the seller asset')
  transport_asset_id: int = Field(description='ID of the transport asset')
  finished_at: datetime = Field(description='Timestamp when the operation was finished')
  history: list[AtsOperationMovement] = Field(description='List of operation movements')
  purchase_orders: list[AtsPurchaseOrder] = Field(description='List of purchase orders')
