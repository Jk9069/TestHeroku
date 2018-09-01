import urllib
import json
import os
import random

from flask import Flask
from flask import request
from flask import make_response

class weatherPlaceRecommendations():
	#from placeTypes search for places in Google Places API
	def requestPlaces(self, weather):
		placeTypes = [
			'park', 'amusement_park', 'aquarium', 'art_gallery',
			'bar', 'bowling_alley', 'cafe', 'department_store',
			'library', 'movie_theater', 'museum', 'night_club', 'restaurant',
			'shopping_mall', 'spa', 'points_of_interest', 'casino'
		]

		#remove outdoor places from recommendations
		if ('Rain' in weather or 'Thunderstorm' in weather):
			placeTypes.remove('park')
			placeTypes.remove('amusement_park')

		#weather not printed?
		print(weather)
		print(len(placeTypes)) #shuold be 17 if weather is sunny

		#coordinates of penang: 5.4356 (lat), 100.3091 (long) - search Penang in general 
		#generate random placeTypes and append to requestLink
		requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&radius=15000&key=AIzaSyBMfB2YS4eye4FNNWvyv71DV5HN3ld8GDs"
		requestLink = (requestLink + "&type=" + placeTypes[random.randint(0, len(placeTypes)-1)])

		print(requestLink)
		
		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		s = json.dumps(placeResult, indent=4, sort_keys = True)
		print(s)
 
		responseText = ""

		#if there are results
		if (placeResult.get("status") == "OK"):
			responseText = "Okay, here goes nothing!"
			#pluck information from placeResult, open now?
			results = placeResult.get("results")

			print(results)

			for items in results:
				print(items["name"])

		elif (placeResult.get("status") == "ZERO_RESULTS"):
			responseText = "No results found :("
			#???

		elif (placeResult.get("status") == "OVER_QUERY_LIMIT"):
			responseText = "Over query limit. Please try again in a few moments"

		#get place ID and get image, website

		return {
			"fulfillmentMessages": [
				{
					"text":{
						"text":[
							responseText
						]
					}
				}
				#{
					#"card": {
						#	"title": "name",
						#	"subtitle": rating? address?,
						#	"imageUri": "image"
							#"buttons": [
							#	{
							#		"text": "More details",
							#		"postback": "url "
							#	}
							#]
						#}
				#}
			],

			"source": 'Google Places API'
		}
