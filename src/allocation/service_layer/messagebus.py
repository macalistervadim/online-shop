from typing import Callable, TYPE_CHECKING

from src.allocation.domain import events
from src.allocation.service_layer import handlers


if TYPE_CHECKING:
    from src.allocation.service_layer import unit_of_work


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            handler(event=events, uow=uow)
            results.append(handler(event=event, uow=uow))
            queue.extend(uow.collect_new_events())
    return results
    

HANDLERS: dict[type[events.Event], list[Callable]] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.AllocationRequired: [handlers.allocate],
    events.BatchCreated: [handlers.add_batch],
}