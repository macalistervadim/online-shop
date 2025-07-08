import pytest

from src.allocation.adapters import repository
from src.allocation.domain import events
from src.allocation.service_layer import messagebus, unit_of_work
from src.allocation.service_layer.exceptions import InvalidSku


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next(
            (
                p
                for p in self._products
                for b in p.batches
                if b.reference == batchref
            ),
            None,
        )

    def list(self):
        return list(self._products)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeUnitOfWorkWithFakeMessagebus(FakeUnitOfWork):
    def __init__(self):
        super().__init__()
        self.events_published: list[events.Event] = []

    def publish_events(self):
        for product in self.products.seen:
            while product.events:
                self.events_published.append(product.events.pop(0))

    def collect_new_events(self):
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                self.events_published.append(event)
                yield event


class TestAddBatch:
    def test_for_new_product(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None),
            uow=uow,
        )
        assert uow.products.get(sku="CRUNCHY-ARMCHAIR") is not None
        assert uow.committed

    def test_for_existing_product(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None),
            uow=uow,
        )
        messagebus.handle(
            event=events.BatchCreated("b2", "CRUNCHY-ARMCHAIR", 99, None),
            uow=uow,
        )
        assert "b2" in [
            b.reference for b in uow.products.get("CRUNCHY-ARMCHAIR").batches
        ]


class TestAllocate:
    def test_returns_allocation(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None),
            uow=uow,
        )
        result = messagebus.handle(
            events.AllocationRequired("o1", "COMPLICATED-LAMP", 10),
            uow=uow,
        )
        assert result == "batch1"

    def test_allocate_commits(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None),
            uow=uow,
        )
        messagebus.handle(
            events.AllocationRequired("o1", "COMPLICATED-LAMP", 10),
            uow=uow,
        )
        assert uow.committed

    def test_allocate_for_invalid_sku(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("b1", "COMPLICATED-LAMP", 100, None),
            uow=uow,
        )
        with pytest.raises(InvalidSku):
            messagebus.handle(
                events.AllocationRequired("o1", "NONEXISTENTSKU", 10),
                uow=uow,
            )


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("batch1", "ADORABLE-SETTEE", 100, None),
            uow=uow,
        )
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        messagebus.handle(
            event=events.BatchQuantityChanged("batch1", 50),
            uow=uow,
        )
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 50

    def test_reallocates_if_necessary(self):
        uow = FakeUnitOfWork()
        event_history = [
            events.BatchCreated("batch1", "ADORABLE-SETTEE", 50, None),
            events.BatchCreated("batch2", "ADORABLE-SETTEE", 50, None),
            events.AllocationRequired("o1", "ADORABLE-SETTEE", 20),
            events.AllocationRequired("o2", "ADORABLE-SETTEE", 20),
        ]
        for event in event_history:
            messagebus.handle(event, uow)
        [batch1, batch2] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        messagebus.handle(
            event=events.BatchQuantityChanged("batch1", 25),
            uow=uow,
        )
        [batch1, batch2] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch1.available_quantity == 5
        assert batch2.available_quantity == 30

    def test_reallocates_if_necessary_isolated(self):
        uow = FakeUnitOfWorkWithFakeMessagebus()

        event_history = [
            events.BatchCreated("batch1", "ADORABLE-SETTEE", 50, None),
            events.BatchCreated("batch2", "ADORABLE-SETTEE", 50, None),
            events.AllocationRequired("o1", "ADORABLE-SETTEE", 20),
            events.AllocationRequired("o2", "ADORABLE-SETTEE", 20),
        ]
        for event in event_history:
            messagebus.handle(event, uow)
        [batch1, batch2] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        messagebus.handle(
            event=events.BatchQuantityChanged("batch1", 25),
            uow=uow,
        )
        [reallocation_event] = uow.events_published
        assert isinstance(reallocation_event, events.AllocationRequired)
        assert reallocation_event.orderid in {"o1", "o2"}
        assert reallocation_event.sku == "ADORABLE-SETTEE"
