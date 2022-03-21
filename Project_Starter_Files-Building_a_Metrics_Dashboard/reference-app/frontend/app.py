from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info("frontend_app_info", "Frontend App Info", version="1.0.3")

@app.route("/")
def homepage():
    return render_template("main.html")

#metrics.register_default(
#    metrics.counter(
#        'by_path_counter', 'Request count by request paths',
#        labels={'path': lambda: request.path}
#    )
#)

if __name__ == "__main__":
    app.run()
