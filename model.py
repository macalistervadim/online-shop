from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(
        self,
        ref: str,
        sku: str,
        qty: int,
        eta: date | None,
    ):
        self.reference = ref
        self.sku = sku
        self.available_quantity = qty
        self.eta = eta

    def allocate(self, line: OrderLine):
        self.available_quantity -= line.qty

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
