import model
from repository import FakeRepository

batch1 = model.Batch("batch1", "SOME-SOFA", qty=10, eta=None)
batch2 = model.Batch("batch2", "SOME-CHAIR", qty=20, eta=None)
batch3 = model.Batch("batch3", "SOME-CHAIR", qty=30, eta=None)
fake_repo = FakeRepository([batch1, batch2, batch3])
