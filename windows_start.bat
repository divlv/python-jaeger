set OTEL_EXPORTER_JAEGER_AGENT_HOST=jaegerdemo.hopto.org
set OTEL_EXPORTER_JAEGER_AGENT_PORT=6831
set REMOTE_URL_TO_CALL=http://remoteservice.hopto.org/api/v1/worker

python app/main.py
