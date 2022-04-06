from flask import Flask, render_template, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import pymongo
from flask_pymongo import PyMongo

from jaeger_client import Config
from flask_opentracing import FlaskTracing
from prometheus_flask_exporter import PrometheusMetrics
from opentracing.ext import tags as ext_tags

import requests
import time

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "example-mongodb"
app.config[
    "MONGO_URI"
] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

mongo = PyMongo(app)

metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info("backend_app_info", "Backend App info", version="1.0.3")

config = Config(
    config={
        'sampler':
        {
            'type:const',
            'param':1
        },
        'logging': True,
        'reporter_batch_size': 1,
    },
    service_name="backend"
)
jaeger_tracer = config.initialize_tracer()

# Trace All requests
tracing = FlaskTracing(jaeger_tracer, True, app)

@app.route("/")
def homepage():
    return "Hello World"

#metrics.register_default(
#    metrics.counter(
#        'by_path_counter', 'Request count by request paths',
#        labels={'path': lambda: request.path}
#    )
#)

@app.route("/api")
def my_api():
    answer = "something"
    return jsonify(repsonse=answer)


@app.route("/star", methods=["POST"])
def add_star():
    star = mongo.db.stars
    name = request.json["name"]
    distance = request.json["distance"]
    star_id = star.insert({"name": name, "distance": distance})
    new_star = star.find_one({"_id": star_id})
    output = {"name": new_star["name"], "distance": new_star["distance"]}
    return jsonify({"result": output})

if __name__ == "__main__":
    app.run()
