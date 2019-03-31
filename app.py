#!/usr/bin/env python
import os
from simpleTodo import APP as application

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8080, application)
    # Wait for a single request, serve it and quit.
    httpd.serve_forever()
