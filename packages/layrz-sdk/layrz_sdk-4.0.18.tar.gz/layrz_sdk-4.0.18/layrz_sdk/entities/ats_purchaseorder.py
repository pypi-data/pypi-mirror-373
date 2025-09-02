"""Entry entity"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class OrderStatus(StrEnum):
  GENERATED = 'GENERATED'
  IN_TRANSIT = 'IN_TRANSIT'
  WAITING_TO_DISPATCH = 'WAITING_TO_DISPATCH'  # For trucks
  DELIVERED = 'DELIVERED'
  # For the purchase order status in the port
  READY_TO_OPERATE = 'READY_TO_OPERATE'
  UNLOADING_OPERATION = 'UNLOADING_OPERATION'
  UNLOADING_FUEL = 'UNLOADING_FUEL'
  UNLOADING_FUEL_INTERRUPTED = 'UNLOADING_FUEL_INTERRUPTED'
  DESTINATION_BERTH_EXIT = 'DESTINATION_BERTH_EXIT'
  ORIGIN_BERTH_EXIT = 'ORIGIN_BERTH_EXIT'


class OrderCategories(StrEnum):
  PICKUP = 'PICKUP'
  PICKUP_TO_SUPPLIER = 'PICKUP_TO_SUPPLIER'
  TRANSFER = 'TRANSFER'
  DELIVERY_TO_SUPPLIER = 'DELIVERY_TO_SUPPLIER'
  DELIVERY_TO_RESELLER = 'DELIVERY_TO_RESELLER'
  FOR_SALE_OUTSIDE = 'FOR_SALE_OUTSIDE'
  DELIVERY_TO_STORAGE = 'DELIVERY_TO_STORAGE'
  RETURN_FROM_STORAGE = 'RETURN_FROM_STORAGE'
  NOT_DEFINED = 'NOT_DEFINED'


class DeliveryCategories(StrEnum):
  SAME_STATE = 'SAME_STATE'
  OTHER_STATE = 'OTHER_STATE'
  NOT_DEFINED = 'NOT_DEFINED'


class AtsPurchaseOrder(BaseModel):
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
  order_id: int = Field(description='ID of the order')
  category: OrderCategories | None = Field(description='Category of the operation', default=None)
  deliver_category: DeliveryCategories | None = Field(description='Delivery category of the operation', default=None)
  seller_asset_id: int = Field(description='ID of the seller asset')
  transport_asset_id: int | None = Field(description='ID of the transport asset', default=None)
  asset_id: int = Field(description='ID of the asset')
  delivered_at: datetime | None = Field(description='Timestamp when the operation was delivered', default=None)
  eta: datetime | None = Field(description='Estimated time of arrival to the destination', default=None)
  eta_updated_at: datetime | None = Field(description='Timestamp when the ETA was last updated', default=None)
  invoice_type: str = Field(description='Type of the invoice')
  operation_id: int | None = Field(description='ID of the operation', default=None)
