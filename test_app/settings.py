DEBUG = True

SECRET_KEY = 'asdf1234'

ROOT_URLCONF = 'test_app.urls'

INSTALLED_APPS = [
    'ansible_observe.opentelemetry'
]

ANSIBLE_OBSERVE_OUTPUT_SPAN_TO_CONSOLE = True

import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": { # Optional: configure the root logger
        "handlers": ["console"],
        "level": "INFO",
    },
}