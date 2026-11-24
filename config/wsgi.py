"""
WSGI config for content_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.conf import settings
from django.core.wsgi import get_wsgi_application

django_application = get_wsgi_application()

if not settings.DEBUG:
    from dj_static import Cling

    django_application = Cling(django_application)

CLEVER_PROXY_IPS = frozenset(
    address.strip() for address in os.getenv("CC_REVERSE_PROXY_IPS", "").split(",") if address.strip()
)


def application(environ, start_response):
    if environ.get("REMOTE_ADDR") in CLEVER_PROXY_IPS:
        # Clever Cloud appends its own Forwarded entry after any client-provided entries.
        forwarded = environ.get("HTTP_FORWARDED", "").rsplit(",", 1)[-1]
        for parameter in forwarded.split(";"):
            name, _, value = parameter.partition("=")
            if name.strip().lower() != "proto":
                continue
            scheme = value.strip().strip('"').lower()
            if scheme in ("http", "https"):
                environ["wsgi.url_scheme"] = scheme
            break

    return django_application(environ, start_response)
