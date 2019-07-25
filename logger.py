import os
import logging
from logging.handlers import TimedRotatingFileHandler

def createLogger(filename, directory, logLevel, loggerName):

	if not os.path.exists(directory):
		os.makedirs(directory)

	format = '%(asctime)s - %(levelname)s - %(message)s'
	formatter = logging.Formatter(format)
	handler = TimedRotatingFileHandler(directory + '\\' + filename,
	                                   when='s',
									   interval=1800,
									   backupCount=100)
	handler.setFormatter(formatter)
	logger = logging.getLogger(loggerName)
	logger.addHandler(handler)
	logger.setLevel(logLevel)
	return logger

baseDirectory = '' # Excluded for security reasons
ACTIVITYLOGGER = createLogger('activity.log', baseDirectory, logging.INFO, 'activity')