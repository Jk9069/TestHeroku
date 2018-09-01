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
			'shopping_mall', 'spa', 'points of interest', 'casino'
		]

		#remove outdoor places from recommendations
		if ('Rain' in weather or 'Thunderstorm' in weather):
			placeTypes.remove('park')
			placeTypes.remove('amusement_park')

		#print(weather)
		#shuold be 17 if weather is sunny, 15 if rainy
		#print(len(placeTypes)) 

		#coordinates of penang: 5.4356 (lat), 100.3091 (long) - search Penang in general 
		#generate random placeTypes and append to requestLink
		requestLink = "https://api.sygictravelapi.com/1.0/en/places/list?parents=city:186&level=poi&limit=100"
		#requestLink = (requestLink + "&type=" + placeTypes[random.randint(0, len(placeTypes))])

		#so that can view actual results on web browser
		print(requestLink)
		
		#post url
		#placeResult = json.loads(urllib.request.urlopen(requestLink).read())
		request = urllib.request.Request(requestLink, headers={'x-api-key':'MbSr78YZnbagZpgKINcfb16CcksWk7zyIF8FMzm5'})
		placeResult = (urllib.request.urlopen(request)).read()

		print(placeResult)

		# #if there are results
		# responseText = ""
		# if (placeResult.get("status") == "OK"):
		# 	responseText = "Okay, here goes nothing!"
		# 	#pluck information from placeResult, open now?
		# 	results = placeResult.get("results")

		# 	print(results)

		# 	for items in results:
		# 		print(item["name"])

		# elif (placeResult.get("status") == "ZERO_RESULTS"):
		# 	responseText = "No results found :("
		# 	#???

		# elif (placeResult.get("status") == "OVER_QUERY_LIMIT"):
		# 	responseText = "Over query limit. Please try again in a few moments"

		# #get place ID and get image, website

		return {
			"fulfillmentMessages": [
				{
					"text":{
						"text":[
							#responseText
							"Here goes nothing..."
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
