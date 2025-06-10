import abc

import src.allocation.domain.model as model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, product_id) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, product: model.Product):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product):
        self.session.add(product)

    def get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).first()
