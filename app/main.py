import ssl
import random
import datetime
import time
import os
import urllib.request
from flask import Flask
from flask import Blueprint
from flask import request as frequest
from flask_cors import CORS
from flask_restplus import Api
from flask_restplus import Resource as ApiResource
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

serviceName = "SpaceX Moon Mission"
remoteAddressToCall = os.getenv("REMOTE_URL_TO_CALL", "https://en.wikipedia.org/wiki/Tracing_(software)")

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: serviceName})
    )
)
tracer = trace.get_tracer(__name__)

# Сreate a JaegerExporter
# Configured via environment variables:
# OTEL_EXPORTER_JAEGER_AGENT_HOST=jaegerdemo.hopto.org
# OTEL_EXPORTER_JAEGER_AGENT_PORT=6831
# See: https://opentelemetry-python.readthedocs.io/en/latest/exporter/jaeger/jaeger.html
jaeger_exporter = JaegerExporter()


# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter)

# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)
# Allow remote calls -- CORS
cors = CORS(app, resources={r"/.*/h*": {"origins": "*"},
                            r"/.*/worker*": {"origins": "*"},
                            r"/.*/nestedworker*": {"origins": "*"},
                            r"/.*/error*": {"origins": "*"},
                            r"/.*/remotecall*": {"origins": "*"}
                            })

# Registering 2 Blueprints for static web and Swagger UI:
default_web = Blueprint("default_web", __name__, url_prefix="", template_folder="templates")


@default_web.route("/")
def home_page():
    return "<html><body>OpenTelemetry Demo w/Python.<br/><br/><a href='/api/'>Go to /api for Swagger UI</a></body></html>"


app.register_blueprint(default_web)

swagger = Blueprint("swagger", __name__, url_prefix="/api")
api = Api(swagger, version="1.0",
          title=serviceName,
          description="Just a sample service (Service1)",
          default="Services",
          default_label="All available services list:")
app.register_blueprint(swagger)

context = ssl._create_unverified_context()


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
        Worker endpoint with some random delay of 2..10 sec. (returns just a random number)
        """
        # Get full URL of the current request
        url = urllib.request.Request(api.url_for(Work, _external=True))

        # Get remote client IP address
        remote_addr = frequest.remote_addr

        with tracer.start_as_current_span(str(url.get_full_url()) + " - Some worker") as span:
            now = datetime.datetime.now()
            span.set_attribute("SPACEX local time", now.strftime("%d/%m/%Y %H:%M:%S"))
            span.set_attribute("WHO's CALLING ME? REMOTE CLIENT IP", str(remote_addr))

            time.sleep(random.randint(2, 10))

        return {'status': 'OK', 'number': random.randint(1, 100)}


api.add_resource(Work, '/v1/worker')


class NestedWork(ApiResource):
    def get(self):
        """
        This Worker contains nested span. Both with some random delay of 2..10 sec. (returns just a random number)
        """
        # Get full URL of the current request
        url = urllib.request.Request(api.url_for(Work, _external=True))
        with tracer.start_as_current_span(str(url.get_full_url()) + " - Envelope worker") as span:
            now = datetime.datetime.now()
            span.set_attribute("SPACEX local time", now.strftime("%d/%m/%Y %H:%M:%S"))
            time.sleep(random.randint(2, 10))
            with tracer.start_as_current_span(str(url.get_full_url()) + " - Nested worker") as span:
                now = datetime.datetime.now()
                span.set_attribute("NESTED SPACEX local time", now.strftime("%d/%m/%Y %H:%M:%S"))
                time.sleep(random.randint(2, 10))

        return {'status': 'OK', 'number': random.randint(1, 100)}


api.add_resource(NestedWork, '/v1/nestedworker')


class WorkError(ApiResource):
    def get(self):
        """
        Worker with 50% error probability (returns random number)
        """
        # Get full URL of the current request
        url = urllib.request.Request(api.url_for(WorkError, _external=True))
        with tracer.start_as_current_span(str(url.get_full_url()) + " - Not stable worker") as span:
            span.set_attribute("Who started me??", "Chuck Norris!")
            if random.randint(1, 100) > 50:
                return 1 / 0

        return {'status': 'OK', 'number': random.randint(1, 100)}


api.add_resource(WorkError, '/v1/error')


class RemoteCall(ApiResource):
    @api.doc(
        description="This worker calls remote resource - " + remoteAddressToCall
    )
    def get(self):
        """
        This worker calls remote resource - URL is configured via ENV vars.(saving remote data in the span)
        """
        # Get full URL of the current request
        url = urllib.request.Request(api.url_for(RemoteCall, _external=True))
        # get from env

        with tracer.start_as_current_span(str(url.get_full_url()) + " - Remote call worker") as span:
            span.set_attribute("CALLING Remote address", remoteAddressToCall)
            # request remote resource

            with urllib.request.urlopen(remoteAddressToCall, context=context) as response:
                html = response.read()
                span.set_attribute("Remote response (100 bytes)", str(html[:100]) + "...")

        return {'Job': 'Done'}


api.add_resource(RemoteCall, '/v1/remotecall')


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
