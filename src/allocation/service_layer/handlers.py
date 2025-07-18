from __future__ import annotations

import src.allocation.domain.model as model
from src.allocation.adapters import redis_eventpublisher
from src.allocation.domain import events
from src.allocation.domain.model import OrderLine
from src.allocation.service_layer import unit_of_work
from src.allocation.service_layer.exceptions import InvalidSku


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    event: events.AllocationRequired,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = OrderLine(event.orderid, event.sku, event.qty)

    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
        return batchref


def deallocate(  # fixme
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
    event: events.BatchCreated,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(sku=event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(
            model.Batch(event.ref, event.sku, event.qty, event.eta),
        )
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock,
    uow: unit_of_work.AbstractUnitOfWork,
):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )


def change_batch_quantity(
    event: events.BatchQuantityChanged,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        product = uow.products.get_by_batchref(batchref=event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
        uow.commit()


def publish_allocated_event(
    event: events.Allocated,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    redis_eventpublisher.publish("line_allocated", event)


def add_allocation_to_read_model(
    event: events.Allocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            "INSERT INTO allocations_view (orderid, sku, batchref)"
            " VALUES (:orderid, :sku, :batchref)",
            dict(
                orderid=event.orderid,
                sku=event.sku,
                batchref=event.batchref,
            ),
        )
        uow.commit()


def remove_allocation_from_read_model(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            "DELETE FROM allocations_view "
            " WHERE orderid = :orderid AND sku = :sku"
        )
