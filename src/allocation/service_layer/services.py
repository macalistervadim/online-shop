from __future__ import annotations

import domain.model as model
from adapters.repository import AbstractRepository
from domain.model import OrderLine

from allocation.service_layer import unit_of_work
from service_layer.exceptions import InvalidSku


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
    repo: AbstractRepository,
    session,
) -> None:
    line = OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    model.deallocate(line, batches)
    session.commit()


def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: str | None,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()
