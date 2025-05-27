import abc

import models.model as model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        self.session.add(batch)

    def get(self, reference) -> model.Batch:
        return (
            self.session.query(model.Batch)
            .filter_by(reference=reference)
            .one()
        )

    def list(self):
        return self.session.query(model.Batch).all()
