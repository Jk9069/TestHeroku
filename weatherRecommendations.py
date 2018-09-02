import urllib
import json
import os
import random

from Place import Place

from flask import Flask
from flask import request
from flask import make_response

class weatherPlaceRecommendations():
	#from placeTypes search for places in Google Places API
	def requestPlaces(self, weather):
		placeTypes = [
			'park', 'amusement_park', 'aquarium', 'art_gallery',
			'bowling_alley', 'library', 'movie_theater', 'museum',
			'shopping_mall', 'spa', 'points_of_interest'
		]

		#remove outdoor places from recommendations
		if ('Rain' in weather or 'Thunderstorm' in weather):
			placeTypes.remove('park')
			placeTypes.remove('amusement_park')

		#weather not printed?
		print(weather)

		#coordinates of penang: 5.4356 (lat), 100.3091 (long) - search Penang in general 
		#generate random placeTypes and append to requestLink
		requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&radius=15000&key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI"
		requestLink = (requestLink + "&type=" + placeTypes[random.randint(0, len(placeTypes)-1)])

		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		s = json.dumps(placeResult, indent=4, sort_keys = True)
		print(requestLink)
		print(s)
 
		responseText = ""
		shortlistPlaces = []

		#if there are results
		if (placeResult.get("status") == "OK"):
			responseText = "Okay, here goes nothing!"

			#pluck information from placeResult, open now?
			#get place ID and get image, website
			results = placeResult.get("results")
			counter = 0;

			for items in results:
				#only get places that are opened now?
				if ("opening_hours" in items):
					openNow = items["opening_hours"].get("open_now", 'false')
				else:
					openNow = 'false'
				
				placeName = items["name"]
				placeID = items["place_id"]

				if ("rating" in items):
					rating = items["rating"]
				else:
					rating = '0'
				
				newPlace = Place(placeID, placeName, rating, openNow)

				#add to array to be displayed
				if (counter < 10):
					shortlistPlaces.append(newPlace)
					counter += 1
					print(newPlace.getRating())
				else:
					break

			data = {"source": "Google Places API", "fulfillmentMessages":[{"text":{"text":[responseText]}} ]}

			for x in range(len(shortlistPlaces)-1):
				place = shortlistPlaces[x]

				data["fulfillmentMessages"].append(
					{
						"card": { 
							 "title": place.getPlaceName(),
							 "subtitle": place.getRating() + "\n" + place.getOpenNow(),
							 "imageUri": "https://maps.gstatic.com/mapfiles/place_api/icons/generic_business-71.png",
							 "buttons": [
							 	{
							 		"text": "More details",
							 		"postback": "https://www.google.com/maps/@5.3590784,100.1863997,11z"
							 	}
							 ]
						}
					}
				)

		elif (placeResult.get("status") == "ZERO_RESULTS"):
			responseText = "No results found :("
			#???

		elif (placeResult.get("status") == "OVER_QUERY_LIMIT"):
			responseText = "Over query limit. Please try again in a few moments"

		#print(json.dumps(data, indent=4))

		return json.dumps(data, indent=4)
			
			# "fulfillmentMessages": [
			# 	{
			# 		"text":{
			# 			"text":[
			# 				responseText
			# 			]
			# 		}
			# 	},

			# 	# {
			# 	# 	"card": {
			# 	# 			"title": "name",
			# 	# 			"subtitle": rating? address?,
			# 	# 			"imageUri": "image"
			# 	# 			"buttons": [
			# 	# 				{
			# 	# 					"text": "More details",
			# 	# 					"postback": "url "
			# 	# 				}
			# 	# 			]
			# 	# 		}
			# 	# }
			# ]
		
