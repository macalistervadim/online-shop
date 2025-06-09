from __future__ import annotations

from datetime import date

import src.allocation.domain.model as model
from src.allocation.domain.model import OrderLine
from src.allocation.service_layer import unit_of_work
from src.allocation.service_layer.exceptions import InvalidSku


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    orderid: str,
    sku: str,
    qty: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = OrderLine(orderid, sku, qty)

    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = model.allocate(line, batches)
        uow.commit()

    return batchref


def deallocate(
    orderid: str,
    sku: str,
    qty: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    line = OrderLine(orderid, sku, qty)

    with uow:
        batches = uow.products.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        model.deallocate(line, batches)
        uow.commit()


def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: date | None,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        uow.products.add(model.Batch(ref, sku, qty, eta))
        uow.commit()
