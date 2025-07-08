import abc

import src.allocation.domain.model as model


class AbstractRepository(abc.ABC):
    def __init__(self) -> None:
        self.seen: set[model.Product] = set()

    def add(self, product: model.Product) -> None:
        self._add(product)
        self.seen.add(product)

    def get(self, sku) -> model.Product:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    def get_by_batchref(self, batchref) -> model.Product:
        product = self._get_by_batchref(batchref)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _get(self, product_id) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_batchref(self, batchref) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product):
        self.session.add(product)

    def _get(self, sku):
        return next(
            (p for p in self.session.query(model.Product) if p.sku == sku),
            None,
        )

    def _get_by_batchref(self, batchref):
        return next(
            (
                p
                for p in self.session.query(model.Product)
                for b in p.batches
                if b.reference == batchref
            ),
            None,
        )
