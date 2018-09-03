import urllib
import json
import os
import random

#Python Image Library
from PIL import Image 
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

				#obtain photo reference to get image to display in cards
				if ("photos" in items):
					photoDeets = items["photos"]

					for x in photoDeets:
						if ("photo_reference" in x):
							photoRef = x.get("photo_reference", 'none')

				#using photo reference to get image
				if (photoRef != 'none'):
					photoRequest = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&key=AIzaSyBMfB2YS4eye4FNNWvyv71DV5HN3ld8GDs&photoreference=" + photoRef
					photoURL = urllib.request.urlopen(photoRequest).geturl()
					#print(photoURL)

				else:
					photoURL = "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png"

				#maybe i should go get types?
				stringTypes = ""
				if ("types" in items):
					types = items["types"]

					for x in types:
						if "_" in x:
							x.replace("_", " ")

						stringTypes += x

						if (x < (len(x) - 1)):
							stringTypes += ", "

				#create the Place object containing all required values
				newPlace = Place(placeID, placeName, rating, openNow, photoRef, photoURL, stringTypes)

				#add to array to be displayed
				if (counter < 10):
					shortlistPlaces.append(newPlace)
					counter += 1
				else:
					break

				
			googleLogo = Image.open("powered_by_google_on_white.png")
			data = {"source": "Google Places API", "fulfillmentMessages":[{"text":{"text":[responseText]}} ]}

			for x in range(len(shortlistPlaces)-1):
				place = shortlistPlaces[x]

				data["fulfillmentMessages"].append(
					{
						"card": { 
							 "title": place.getPlaceName(),
							 "subtitle": place.getRating() + "\n" + place.getOpenNow() + "\n" + place.getPlaceTypes(), #+ "\n" + googleLogo.show(),
							 "imageUri": place.getPhotoURL(),
							 "buttons": [
							 	{
							 		"text": "More details",
							 		#link to open in google maps
							 		"postback": "https://www.google.com/maps/search/?api=1&query=" + place.getPlaceName() + "&query_place_id=" + place.getPlaceID()
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

		else: 
			responseText = ""

		print(len(shortlistPlaces))

		return data
			
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
		
