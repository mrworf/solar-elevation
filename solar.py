#!/usr/bin/env python3

from flask import Flask, request, jsonify
import pvlib
import pandas as pd
import os
import sys

app = Flask(__name__)

# Load location and colors from environment variables or exit with error
try:
	latitude = float(os.environ['SOLAR_LATITUDE'])
	longitude = float(os.environ['SOLAR_LONGITUDE'])
except (KeyError, ValueError):
	print("Warning: SOLAR_LATITUDE and SOLAR_LONGITUDE environment variables must be set with valid numbers")
	sys.exit(1)

try:
	colors = {
		'night': [int(x) for x in os.environ.get('SOLAR_COLOR_NIGHT', '1,1,10,10').split(',')],
		'morning': [int(x) for x in os.environ.get('SOLAR_COLOR_MORNING', '5,5,40,50').split(',')],
		'noon': [int(x) for x in os.environ.get('SOLAR_COLOR_NOON', '255,255,251,255').split(',')]
	}
	# Validate all color arrays have 4 values
	if not all(len(color) == 4 for color in colors.values()):
		raise ValueError("All color arrays must contain exactly 4 values")
except ValueError as e:
	print(f"Warning: Invalid color format in environment variables: {str(e)}")
	print("Colors should be comma-separated integers (RGBW format)")
	sys.exit(1)

def interpolate_arrays(array1, array2, minimum, maximum, current):
	# Ensure current is within the bounds [minimum, maximum]
	current = max(minimum, min(current, maximum))

	# Calculate interpolation ratio
	ratio = (current - minimum) / float(maximum - minimum)

	# Interpolate between each pair of values in the arrays
	interpolated = [
		int((1 - ratio) * val1 + ratio * val2)
		for val1, val2 in zip(array1, array2)
	]

	# Clamp each value to be within the 0-255 range, if necessary
	interpolated = [max(0, min(255, val)) for val in interpolated]

	return interpolated

def get_max_elevation():
	try:
		# Specify the date for which you want to calculate solar elevation
		time = pd.Timestamp.now(tz='US/Pacific')
		date = time.date()
		# Lets get a range so we can find the peak
		timestamps = pd.date_range(start=date, periods=24*60, freq="T")
		# Create a solar position model (SPA) instance
		solar_position_max = pvlib.solarposition.get_solarposition(timestamps, latitude, longitude)
		solar_position_now = pvlib.solarposition.get_solarposition(time, latitude, longitude)
		# Get the solar elevation at solar noon
		solar_elevation_now = solar_position_now['elevation'].max()
		solar_elevation_max = solar_position_max['elevation'].max()
		return {'max':solar_elevation_max, 'now':solar_elevation_now}
	except Exception as e:
		return repr({'error': str(e)}), 500

@app.route('/rgbw')
def get_rgbw_for_elevation():
	elevation = get_max_elevation()
	#elevation['now'] = elevation['max']
	#print(repr(elevation))
	color = None
	if elevation['now'] > 0:
		color = interpolate_arrays(colors['morning'], colors['noon'], 0, elevation['max'], elevation['now'])
	else:
		color = interpolate_arrays(colors['night'], colors['morning'], -18, 0, elevation['now'])
	if color is None:
		color = colors['night'] # Sanity!
	return jsonify({'rgbw':color})

if __name__ == '__main__':
	app.run(debug=False, port=6060, host='0.0.0.0')

