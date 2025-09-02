from typing import Optional

import httpx
from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.tortoiseorm import TortoiseORMInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from pydantic import Field
from pydantic_settings import BaseSettings


class OpenTelemetrySettings(BaseSettings):
    """
    跟踪和指标配置
    """
    ENDPOINT: Optional[str] = Field(default=None, description="访问接口", example="http://127.0.0.1")
    AUTHORIZATION: Optional[str] = Field(default=None, description="认证字符串")

    def setup_open_telemetry(self, app: FastAPI, service_name: str):
        if not self.ENDPOINT:
            return

        with httpx.Client() as client:
            health_check = client.get(f"{self.ENDPOINT}/healthz", timeout=3).json()
            if health_check["status"] != "ok":
                raise Exception("otlp服务异常")
            resource = Resource(attributes={
                SERVICE_NAME: service_name
            })

            tracer_provider = TracerProvider(resource=resource)
            headers = {
                "Authorization": self.AUTHORIZATION} if self.AUTHORIZATION else {}
            exporter = OTLPMetricExporter(
                endpoint=f"{self.ENDPOINT}/api/default/v1/metrics",
                headers=headers,
            )
            meter_provider = MeterProvider([PeriodicExportingMetricReader(exporter)], resource=resource)
            metrics.set_meter_provider(meter_provider)
            processor = BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=f"{self.ENDPOINT}/api/default/v1/traces",
                    headers=headers
                )
            )
            tracer_provider.add_span_processor(processor)
            trace.set_tracer_provider(tracer_provider)
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=tracer_provider,
                meter_provider=meter_provider,
            )
            TortoiseORMInstrumentor().instrument(tracer_provider=tracer_provider)
            HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)

    class Config:
        env_prefix = 'OTLP_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'
