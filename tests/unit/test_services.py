from datetime import date, timedelta

import adapters.repository as repository
import domain.model as model
import pytest
import service_layer.services as services

from allocation.service_layer import unit_of_work

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def test_add_batch():
        uow = FakeUnitOfWork()
        services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
        assert uow.batches.get("b1") is not None
        assert uow.commited

    def test_allocate_returns_allocation():
        uow = FakeUnitOfWork()
        services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
        result = services.allocate("01", "COMPLICATED-LAMP", 10, uow)
        assert result == "batch1"


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)
    services.allocate("01", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    services.allocate("01", "BLUE-PLINTH", 10, repo, session)
    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90
    services.deallocate("01", "BLUE-PLINTH", 10, repo, session)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    services.add_batch("b2", "RED-PLINTH", 100, None, repo, session)
    services.allocate("01", "RED-PLINTH", 10, repo, session)
    batch_blue = repo.get(reference="b1")
    batch_red = repo.get(reference="b2")
    assert batch_blue.available_quantity == 100
    assert batch_red.available_quantity == 90
    services.deallocate("01", "RED-PLINTH", 10, repo, session)
    assert batch_blue.available_quantity == 100
    assert batch_red.available_quantity == 100


def test_trying_to_deallocate_unallocated_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    with pytest.raises(model.CannotDeallocate):
        services.deallocate("O1", "BLUE-PLINTH", 10, repo, session)


def test_prefers_current_stock_batches_to_shipments():
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch(
        "in-stock-batch",
        "RETRO-CLOCK",
        100,
        None,
        repo,
        session,
    )
    services.add_batch(
        "shipment-batch",
        "RETRO-CLOCK",
        100,
        eta=tomorrow,
        repo=repo,
        session=session,
    )

    services.allocate("oref", "RETRO-CLOCK", 10, repo, session)

    assert repo.get("in-stock-batch").available_quantity == 90
    assert repo.get("shipment-batch").available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(
        "in-stock-batch",
        "RETRO-CLOCK",
        100,
        None,
        repo,
        session,
    )
    services.add_batch(
        "shipment-batch",
        "RETRO-CLOCK",
        100,
        eta=tomorrow,
        repo=repo,
        session=session,
    )
    services.allocate("oref", "RETRO-CLOCK", 10, repo, session)

    assert repo.get("in-stock-batch").available_quantity == 90
    assert repo.get("shipment-batch").available_quantity == 100


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("01", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(
        services.InvalidSku,
        match="Invalid sku NONEXISTENTSKU",
    ):
        services.allocate("01", "NONEXISTENTSKU", 10, repo, session)
