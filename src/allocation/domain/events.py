from dataclasses import dataclass


class Event:
    pass


@dataclass
class OutOfStock(Event):
    sku: str


@dataclass
class BatchCreated(Event):
    ref: str
    sku: str
    qty: int
    eta: str | None = None
    

@dataclass
class AllocationRequired(Event):
    orderid: str
    sku: str
    qty: int
    
    
@dataclass
class BatchQuantityChanged(Event):
    ref: str
    qty: int