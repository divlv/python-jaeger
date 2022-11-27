# OpenTelemetry Demo w/Python

This is sample demo Python project which illustrates how Open Telemetry works.
As an OpenTelemetry API implementation in our case is [Jaeger](https://www.jaegertracing.io/).

                                 
To simplify the demo we'll use free DNS names from [noip.com](https://www.noip.com/).

Let's use NoIP's "**hopto.org**" zone for our demo purposes.


### Hosts
In this demo we will use 3 hosts:
- **localhost** (for starting python-jaeger application)
- **remoteservice.hopto.org** (for starting 2nd instance if python-jaeger application, i.e. some remote service to call from the 1st service, which is running on localhost) and
- **jaegerdemo.hopto.org** (Jaeger UI, data collector)


Run Jaeger in Docker. Use `--net=host` to simplify the ports-related stuff. Security if out of this demo scope. (Ahh, you always got IPTables, right?! ;-) )  

```bash
docker run -it --net=host jaegertracing/all-in-one:latest
```

Then go to http://jaegerdemo.hopto.org:16686 and we're here.

                          

docker run -it --net=host -e REMOTE_URL_TO_CALL=jaegerdemo.hopto.org -e OTEL_EXPORTER_JAEGER_AGENT_HOST=jaegerdemo.hopto.org -e OTEL_EXPORTER_JAEGER_AGENT_PORT=6831 dimedrol/python-jaeger

http://remoteservice.hopto.org/