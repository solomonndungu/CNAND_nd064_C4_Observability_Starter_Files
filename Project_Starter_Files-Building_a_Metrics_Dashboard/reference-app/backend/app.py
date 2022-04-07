from flask import Flask, render_template, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import pymongo
from flask_pymongo import PyMongo

from jaeger_client import Config
from prometheus_flask_exporter import PrometheusMetrics


import time, random, logging
fromm os import getenv

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "example-mongodb"
app.config[
    "MONGO_URI"
] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

mongo = PyMongo(app)

metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info("backend_app_info", "Backend App info", version="1.0.3")

metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

by_endpoint_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by request endpoint',
    labels={'endpoint':lambda: request.endpoint}
)

JAEGER_AGENT_HOST = getenv('JAEGER_AGENT_HOST', 'localhost')

config = Config(
    config={
        'sampler':
        {
            'type': 'const',
            'param':1
        },
        'logging': True,
        'local_agent': {
            'reporting_host': JAEGER_AGENT_HOST
        },
    },
    service_name="backend"
)
tracer = config.initialize_tracer()

@app.route("/")
@by_endpoint_counter
def homepage():
    with tracer.start_span('hello-world'):
     return "Hello World"

#metrics.register_default(
#    metrics.counter(
#        'by_path_counter', 'Request count by request paths',
#        labels={'path': lambda: request.path}
#    )
#)

@app.route("/api")
@by_endpoint_counter
def my_api():
    with tracer.start_span('api'):
        answer = "something"
        return jsonify(repsonse=answer)

# This will return 405 error
@app.route("/star", methods=["POST"])
@by_endpoint_counter
def add_star():
    star = mongo.db.stars
    name = request.json["name"]
    distance = request.json["distance"]
    star_id = star.insert({"name": name, "distance": distance})
    new_star = star.find_one({"_id": star_id})
    output = {"name": new_star["name"], "distance": new_star["distance"]}
    return jsonify({"result": output})

if __name__ == "__main__":
    app.run(threaded=True)
