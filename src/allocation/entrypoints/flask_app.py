from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.allocation.adapters.orm as orm
import src.allocation.config as config
from src.allocation.domain import events
from src.allocation.service_layer import unit_of_work, messagebus
from src.allocation.service_layer.exceptions import InvalidSku

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        event = events.AllocationRequired(
            orderid=request.json["orderid"],
            sku=request.json["sku"],
            qty=request.json["qty"],
        )
        results = messagebus.handle(event=event, uow=unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)
    except InvalidSku as e:
        return {"message": str(e)}, 422
    
    return {"batchref": batchref}, 201
        

@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        datetime.fromisoformat(eta).date()
        
    event = events.BatchCreated(
        ref=request.json["ref"],
        sku=request.json["sku"],
        qty=request.json["qty"],
        eta=eta,
    )
    messagebus.handle(event=event, uow=unit_of_work.SqlAlchemyUnitOfWork())
    
    return "OK", 201

