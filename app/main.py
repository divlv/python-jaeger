import ssl
import random
import datetime
from flask import Flask
from flask_cors import CORS
from flask_restplus import Resource, Api

app = Flask(__name__)


api = Api(app, version="1.0",
          title="Service1 REST service",
          doc="/api/",
          description="Just a sample service (Service1)",
          default="Services",
          default_label="All available services list:")

context = ssl._create_unverified_context()


class HealthCheck(Resource):
    def get(self):
        """
        Service1 health check
        """
        return {'status': 'UP', 'build': 'GIT_VERSION', 'serverTime': str(datetime.datetime.now()), 'tag': '#GTO'}

api.add_resource(HealthCheck, '/h')


class Work(Resource):
    def get(self):
        """
        Sample worker with some delay (returns random number)
        """
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
