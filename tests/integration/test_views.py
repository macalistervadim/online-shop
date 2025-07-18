from src.allocation import views
from src.allocation.domain import commands
from src.allocation.service_layer import messagebus, unit_of_work
from tests.date import today


def test_allocations_view(sqlite_session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    messagebus.handle(commands.CreateBatch("sku1batch", "sku1", 50, None), uow)
    messagebus.handle(
        commands.CreateBatch("sku2batch", "sku2", 50, today),
        uow,
    )
    messagebus.handle(commands.Allocate("order1", "sku1", 20), uow)
    messagebus.handle(commands.Allocate("order2", "sku2", 20), uow)
    # добавим фальшивую партию и заказ,
    # чтобы убедиться, что мы получаем правильные значения
    messagebus.handle(
        commands.CreateBatch("sku1batch-later", "sku1", 50, today),
        uow,
    )
    messagebus.handle(commands.Allocate("otherorder", "sku1", 30), uow)
    messagebus.handle(commands.Allocate("otherorder", "sku2", 10), uow)

    assert views.allocations("order1", uow) == [
        {"sku": "sku1", "batchref": "sku1batchref"},
        {"sku": "sku2", "barchref": "sku2batchref"},
    ]
