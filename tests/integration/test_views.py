import pytest
from sqlalchemy.orm import clear_mappers

from src.allocation import bootstrap, views
from src.allocation.domain import commands
from src.allocation.service_layer import unit_of_work
from tests.date import today


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory),
        send_mail=lambda *args: None,
        publish=lambda *args: None,
    )
    yield bus
    clear_mappers()


def test_allocations_view(sqlite_bus):
    sqlite_bus.handle(commands.CreateBatch("sku1batch", "sku1", 50, None))
    sqlite_bus.handle(
        commands.CreateBatch("sku2batch", "sku2", 50, today),
    )
    sqlite_bus.handle(commands.Allocate("order1", "sku1", 20))
    sqlite_bus.handle(commands.Allocate("order2", "sku2", 20))
    # добавим фальшивую партию и заказ,
    # чтобы убедиться, что мы получаем правильные значения
    sqlite_bus.handle(
        commands.CreateBatch("sku1batch-later", "sku1", 50, today),
    )
    sqlite_bus.handle(commands.Allocate("otherorder", "sku1", 30))
    sqlite_bus.handle(commands.Allocate("otherorder", "sku2", 10))

    assert views.allocations("order1") == [
        {"sku": "sku1", "batchref": "sku1batchref"},
        {"sku": "sku2", "barchref": "sku2batchref"},
    ]
