from __future__ import annotations

import domain.model as model
from adapters.repository import AbstractRepository
from domain.model import OrderLine
from service_layer.exceptions import InvalidSku


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(line: OrderLine, repo: AbstractRepository, session) -> None:
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
    repo: AbstractRepository,
    session,
) -> None:
    new_batch = model.Batch(ref, sku, qty, eta)
    repo.add(new_batch)
    session.commit()
