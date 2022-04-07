from flask import Flask, render_template, request
import threading
import requests
import random
import time
from prometheus_flask_exporter import PrometheusMetrics
import logging
from jaeger_client import Config

app = Flask(__name__)
metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info("frontend_app_info", "Frontend App Info", version="1.0.3")

metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

by_endpoint_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by request endpoint',
    labels={'endpoint': lambda: request.endpoint}
)

config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    },
    service_name='frontend'
)

tracer= config.initialize_tracer()

@app.route("/")
@by_endpoint_counter
def homepage():
    with tracer.start_span('html'):
        return render_template("main.html")

#metrics.register_default(
#    metrics.counter(
#        'by_path_counter', 'Request count by request paths',
#        labels={'path': lambda: request.path}
#    )
#)

if __name__ == "__main__":
    app.run()
