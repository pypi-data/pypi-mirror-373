"""
======
Server
======


"""

import sys
import os
import time
import socketserver
import logging
from wsgiref import simple_server
from django.core.wsgi import get_wsgi_application
from radiant.wrapper.android.permissions import Permission


class ThreadedWSGIServer(socketserver.ThreadingMixIn, simple_server.WSGIServer):
    """Start Django in multithreaded mode

    It allows for debugging Django while serving multiple requests at once in
    multi-threaded mode.
    """
    pass


# ----------------------------------------------------------------------
def set_permissions(permissions):
    """"""
    _permissions = [getattr(Permission, permission) for permission in [permissions]]
    new_permissions = [permission
                       for permission in _permissions
                       if not Permission.check_permission(permission)]
    if new_permissions:
        Permission.request_permissions(new_permissions)
        while not Permission.check_permission(new_permissions[-1]):
            time.sleep(0.1)


# ----------------------------------------------------------------------
def main(project, ip='localhost', port=5000):
    """"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project}.settings")
    os.environ.setdefault("FRAMEWORK", "django")
    httpd = simple_server.make_server('localhost', 5000, get_wsgi_application(), server_class=ThreadedWSGIServer)
    httpd.serve_forever()
    logging.info("Radiant serving on {}:{}".format(*httpd.server_address))

