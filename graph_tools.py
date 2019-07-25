import itertools
import datetime
from dictionaries import num_to_str_date, num_to_str_weekday


def getHoverInfo(x_data, z_data, max_data):
	"""Determine the hover text for the node"""
	
	text = []
	for counter, row_data in enumerate(z_data):
		temp_text = []
		for row_counter, element in enumerate(row_data):
			hour_data = (counter * 24 / 1440) * 1.00
			time_data = str(hour_data).split('.')
			hour = time_data[0]
			temp_data = "." + time_data[1]
			minute = str(int(float(temp_data) * 60))
			temp_text.append('Day: {0}<br />Hour: {1}<br />Minute: {2:2.2}<br />Data: {3}'.format(
							x_data[row_counter], hour, minute, element))
		text.append(temp_text)
	return text

def getXYZData(query_res):
	"""Graph heatmap data based on certain number of days"""

	try:
		if query_res and len(query_res) > 0:
				
			#create the initial values for the x-axis
			day_init     = query_res[0]['Day']
			weekDay_init = num_to_str_weekday[str(query_res[0]['WeekDay'])]
			month_init   = num_to_str_date[str(query_res [0]['Month'])]
			
			#create the initial lists for creating data
			infoString_init = " ".join (
									[
									weekDay_init,
									month_init,
									str (day_init)
									]
								)
			x_axis             = [infoString_init ]
			z_axis             = []                                                          
			day_data           = []
			num_days, max_data = 1, 0
			
			#get the last entry in the list
			end_entry = query_res [ -1 ]
			day_bucket = ['NaN'] * 1440
			
			#iterate through every result 
			for it_num , entry in enumerate(query_res):
				
				#read the values from the results item
				day        = entry              [           'Day'             ]
				hour       = entry              [           'Hour'            ]
				minute     = entry              [          'Minute'           ]
				weekDay    = num_to_str_weekday [ str ( entry [ 'WeekDay' ] ) ]
				month      = num_to_str_date    [ str ( entry [  'Month'  ] ) ]
				
				bucketVal = (int(hour) * 60) + int(minute)
				
				#see if the day has changed --> if so:
				# 1. add the new string to the x-axis
				# 2. add the day data to the z-axis data
				# 3. clear out the temporary list for the data for the day
				# 4. change the comparision day
				# 5. clear out the bucket containing the day data
				if day != day_init:
					
					infoString = " ".join ([
										weekDay,
										month,
										str(day)
									])
					x_axis.append ( infoString )
					z_axis.append ( day_bucket )
					day_bucket = ['NaN'] * 1440
					day_init   = day
					num_days   = num_days + 1
				
				#add the entry to the the data for the day
				day_bucket[bucketVal] = entry['Data']
				
				#if we are at the last entry, append the last
				#day data to the final entry in the z-axis
				if entry == end_entry:
					z_axis.append ( day_bucket )
					
			if max_data == 0:
				max_data = 1
		
			new_axis = z_axis.copy()
			for element_num, element in enumerate(new_axis):
				last_point = 0
				for counter, entity in enumerate(element):
					if entity != 'NaN':
						for changed_entity in range(last_point, counter):
							z_axis[element_num][changed_entity] = entity
						last_point = counter + 1
				
			y_axis=[24 / 1440 * point for point in range(1440)]
			z_axis = list ( itertools.zip_longest ( *z_axis , fillvalue='NaN' ) )
			return x_axis, y_axis, z_axis, max_data, query_res
		else:
			return [], [], [], 0, []
	except:
		return [], [], [], 0, []
		
def getXYZDataFromCached(current_data, last_data):
	"""Add the current data to the last data and then generate new XYZ data"""

	for data in current_data:
		if data not in last_data:
			last_data.append(data)
		
	x_axis, y_axis, z_axis, max_data, query_res = getXYZData(last_data)
	return x_axis, y_axis, z_axis, max_data, query_res