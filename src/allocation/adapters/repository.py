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

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return (
            self.session.query(model.Batch)
            .filter_by(reference=reference)
            .one()
        )

    def list(self):
        return self.session.query(model.Batch).all()
