from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

import logging

logger = logging.getLogger()

def index(request):
    logger.info("Hello World. This is an info level log message")
    return HttpResponse("Hello, world. You're at the test app index.")
