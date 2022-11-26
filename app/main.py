import ssl
import random
import datetime
import time

from flask import Flask
from flask import Blueprint
from flask_cors import CORS
from flask_restplus import Api, fields
from flask_restplus import Resource as ApiResource
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(
TracerProvider(
        resource=Resource.create({SERVICE_NAME: "my-helloworld-service"})
    )
)
tracer = trace.get_tracer(__name__)

# create a JaegerExporter
jaeger_exporter = JaegerExporter(
    # configure agent
    agent_host_name='localhost',
    agent_port=6831,
    # optional: configure also collector
    # collector_endpoint='http://localhost:14268/api/traces?format=jaeger.thrift',
    # username=xxxx, # optional
    # password=xxxx, # optional
    # max_tag_value_length=None # optional
)

# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter)

# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)


app = Flask(__name__)

default_web = Blueprint(
    "default_web", __name__, url_prefix="", template_folder="templates"
)


@default_web.route("/")
def home_page():
    return "<html><body>Hello World!<br/><br/><a href='/api/'>Go to /api for Swagger</a></body></html>"


app.register_blueprint(default_web)


swagger = Blueprint("swagger", __name__, url_prefix="/api")


api = Api(swagger, version="1.0",
          title="Service1 REST service",
          description="Just a sample service (Service1)",
          default="Services",
          default_label="All available services list:")



context = ssl._create_unverified_context()


app.register_blueprint(swagger)


class HealthCheck(ApiResource):
    def get(self):
        """
        Service1 health check
        """
        return {'status': 'UP', 'serverTime': str(datetime.datetime.now()), 'tag': '#GTO'}

api.add_resource(HealthCheck, '/h')


class Work(ApiResource):
    def get(self):
        """
        Sample worker with some random delay (returns random number)
        """
        with tracer.start_as_current_span("My Work"):
            time.sleep(random.randint(2, 3))

        return {'status': 'OK', 'number': random.randint(1, 100)}


api.add_resource(Work, '/v1/worker')


#
@app.errorhandler(404)
def pageNotFound(e):
    return "Page not found"


@app.errorhandler(500)
def internalServerError(e):
    return "Internal server error"


# Uncomment this line, if running in Development environment
# i.e. not with Gunicorn
app.run(host='0.0.0.0', port='8080')
