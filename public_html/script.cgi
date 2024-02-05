#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from script import app

CGIHandler().run(app)
