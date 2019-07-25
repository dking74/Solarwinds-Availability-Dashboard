#!/usr/bin/env python
# -*- coding utf-8 -*-

from layout import createInitialDashboard
from logger import ACTIVITYLOGGER
from flask import send_from_directory, request
import flask
import os
	
# create the inital dashboard	
server = flask.Flask(__name__)
server.secret_key = b'' # Excluded for security reasons
dashboard = createInitialDashboard(server)

# Disable validation and callback exceptions
dashboard.config.disable_component_validation = True
dashboard.config.suppress_callback_exceptions = True
dashboard.config.suppress_validation_exceptions = True

@dashboard.server.before_request
def initialize():
	"""Function to print the viewer in the log"""
	
	ACTIVITYLOGGER.info(request.environ.get('HTTP_X_REAL_IP', request.remote_addr) + " viewed page")

def suppress_messages():
	"""To suppress messages from Flask"""
	
	import logging
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)
	log.disabled = True
	dashboard.logger.disabled = True
	dashboard.config.suppress_callback_exceptions = True	
	
def main ( ):
	"""Main entry point for program"""

	#suppress_messages()
	dashboard.runDashboard(host='0.0.0.0', port=8080)

	
if __name__ == "__main__":
	main ( )