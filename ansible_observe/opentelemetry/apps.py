from django.apps import AppConfig
from .instrument import setup_tracing

class ActivitystreamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ansible_observe.opentelemetry'
    label = 'dao_opentelemetry'
    verbose_name = 'Auto-Instrumented OpenTelemetry'


    def ready(self):
        setup_tracing()
        super().ready()
