class BadLoginInformation ( Exception ):
	"""Exception to be raised when user provides
	   bad login information to Solarwinds"""
	
	def __init__ ( self, username, password ):
	
		"""
			Method Name: __init__
			Method Purpose: To create a BadLogin Exception
			
			Parameters:
				- username (string): The username logged in with
				- password (string): The password logged in with
				
			Returns: None
		"""
	
		self.__username = username
		self.__password = password 
				
	def __str__ ( self ):
		
		"""Provide a string representation of the exception"""
		return repr ( "The username '{}' and password '{}' combination " \
		        "do not match any records".format ( self.__username, self.__password ) )

class BadEntityType(Exception):
	"""Exception to be raise when user enters inappopriate entity type"""
	
	pass