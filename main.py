#!/usr/bin/env python
import os.path
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import logging
import csv
import re

from py2neo import neo4j
from py2neo import node, rel, cypher
from py2neo.packages.urimagic import URI
import sys
from models import *

from utils import *
from handlers.handlers import *

reload(sys)
sys.setdefaultencoding('utf-8')

# import and define tornado-y things
from tornado.options import define
define("port", default=5000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        self.query_builder = QueryBuilder()
        self.data = DataLoader()
        handlers = [
            (r"/?", MainHandler),
            (r"/2/?", MainHandler2)
            #(r"/load/?", LoadHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)

    # start it up
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
