# OpenTelemetry Demo w/Python

This is sample demo Python project which illustrates how Open Telemetry works.
As an OpenTelemetry API implementation we'll use [Jaeger](https://www.jaegertracing.io/).

                                 
To simplify the demo we'll use free DNS names from [noip.com](https://www.noip.com/).

Let's assume, we have "_jaegerdemo.hopto.org_" host for Jaeger (data collector) UI.



Run Jaeger in Docker. Use `--net=host` to simplify the ports-related stuff. Security if out of this demo scope. (Ahh, you always got IPTables, right?! ;-) )  

```bash
docker run -it --net=host jaegertracing/all-in-one:latest
```

Then go to http://jaegerdemo.hopto.org:16686 and we're here.

                          

docker run -it --net=host -e REMOTE_URL_TO_CALL=jaegerdemo.hopto.org -e OTEL_EXPORTER_JAEGER_AGENT_HOST=jaegerdemo.hopto.org -e OTEL_EXPORTER_JAEGER_AGENT_PORT=6831 dimedrol/python-jaeger

http://remoteservice.hopto.org/