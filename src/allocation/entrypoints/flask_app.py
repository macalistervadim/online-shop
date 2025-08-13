from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.allocation.config as config
from src.allocation import bootstrap
from src.allocation.domain import commands, events
from src.allocation.service_layer import messagebus, unit_of_work
from src.allocation.service_layer.exceptions import InvalidSku

get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        event = events.AllocationRequired(
            orderid=request.json["orderid"],
            sku=request.json["sku"],
            qty=request.json["qty"],
        )
        results = messagebus.handle(
            message=event,
            uow=unit_of_work.SqlAlchemyUnitOfWork(),
        )
        batchref = results.pop(0)
    except InvalidSku as e:
        return {"message": str(e)}, 422

    return {"batchref": batchref}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        datetime.fromisoformat(eta).date()

    cmd = commands.CreateBatch(
        request.json("ref"),
        request.json("sku"),
        request.json("qty"),
        eta,
    )
    bus.handle(cmd)

    return "OK", 201


@app.route("/allocations/<orderid>", methods=["GET"])
def allocations_view_endpoint(orderid):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return "not found"
    return jsonify(result), 200
