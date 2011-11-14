#!/usr/bin/env twistd -ny

import os
import time
import cyclone.web
from twisted.application import service, internet
from twisted.python import log
from twisted.internet import task

class MainHandler(cyclone.web.RequestHandler):
	def get(self):
		self.render("static/index.html")

class MyEventHandler(cyclone.web.SSEHandler):
"""
	This example prints the time directly to the browser using ServerSentEvents.
	To show off the stream, the method bind() fired a looping call that sends the date/time
"""

	def _send(self):
		self.sendEvent('<b>%s</b><br>' % (time.ctime()))
		
	def bind(self):
		self.sendEvent('Initial event')
		loopingCall = task.LoopingCall(self._send)
		loopingCall.start(1, False)

settings = dict(
    cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    static_path=os.path.join(os.path.dirname(__file__), "static"),
  )

webapp = cyclone.web.Application([
  (r"/", MainHandler),
  (r"/events", MyEventHandler),
], **settings)

application = service.Application("cyclone")
cycloneService = internet.TCPServer(8000, webapp)
cycloneService.setServiceParent(application)
