from datetime import date, timedelta

import pytest

import adapters.repository as repository
import domain.model as model
import service_layer.services as services

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


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(
        services.InvalidSku,
        match="Invalid sku NONEXISTENTSKU",
    ):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    line = model.OrderLine("o1", "BLUE-PLINTH", 10)
    services.allocate(line, repo, session)
    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90
    services.deallocate(line, repo, session)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    services.add_batch("b2", "RED-PLINTH", 100, None, repo, session)
    line = model.OrderLine("o1", "RED-PLINTH", 10)
    services.allocate(line, repo, session)
    batch_blue = repo.get(reference="b1")
    batch_red = repo.get(reference="b2")
    assert batch_blue.available_quantity == 100
    assert batch_red.available_quantity == 90
    services.deallocate(line, repo, session)
    assert batch_blue.available_quantity == 100
    assert batch_red.available_quantity == 100


def test_trying_to_deallocate_unallocated_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    line = model.OrderLine("o1", "BLUE-PLINTH", 10)
    with pytest.raises(model.CannotDeallocate):
        services.deallocate(line, repo, session)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = model.Batch(
        "in-stock-batch",
        "RETRO-CLOCK",
        100,
        eta=None,
    )
    shipment_batch = model.Batch(
        "shipment-batch",
        "RETRO-CLOCK",
        100,
        eta=tomorrow,
    )
    line = model.OrderLine("oref", "RETRO-CLOCK", 10)
    model.allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = model.Batch(
        "in-stock-batch", "RETRO-CLOCK", 100, eta=None
    )
    shipment_batch = model.Batch(
        "shipment-batch",
        "RETRO-CLOCK",
        100,
        eta=tomorrow,
    )
    repo = FakeRepository([in_stock_batch, shipment_batch])
    session = FakeSession()

    line = model.OrderLine("oref", "RETRO-CLOCK", 10)

    services.allocate(line, repo, session)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
