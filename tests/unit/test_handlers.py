import pytest

from src.allocation.adapters import repository
from src.allocation.domain import events
from src.allocation.service_layer import unit_of_work, messagebus
from src.allocation.service_layer.exceptions import InvalidSku


class FakeRepository(repository.AbstractRepository):
    
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._batches if p.sku == sku), None)

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

class AddBatch:
    
    def test_for_new_product(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None),
            uow=uow
        )
        assert uow.products.get(sku="CRUNCHY-ARMCHAIR") is not None
        assert uow.committed
        
    def test_for_existing_product(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            event=events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None),
            uow=uow
        )
        messagebus.handle(
            event=events.BatchCreated("b2", "CRUNCHY-ARMCHAIR", 99, None),
            uow=uow
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