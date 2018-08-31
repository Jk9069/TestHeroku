import urllib
import json
import os
import random

from flask import Flask
from flask import request
from flask import make_response

class weatherPlaceRecommendations():
	def __init__ (self, weather):
		self.weather = weather

	#from placeTypes search for places in Google Places API
	def requestPlaces(self):
		placeTypes = [
			'zoo', 'park', 'amusement_park', 'aquarium', 'art_gallery',
			'bar', 'bowling_alley', 'cafe', 'department_store',
			'library', 'movie_theater', 'museum', 'night_club', 'restaurant',
			'shopping_mall', 'spa', 'points of interest', 'casino'
		]

		#remove outdoor places from recommendations
		if ('Rain' in self.weather or 'Thunderstorm' in self.weather):
			placeTypes.remove('zoo')
			placeTypes.remove('park')
			placeTypes.remove('amusement_park')

		placeNames = []

		print(self.weather)
		print(len(placeTypes))

		#coordinates of penang: 5.285153 (lat), 100.456238 (long) - search Penang in general 
		requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&radius=15000&key=AIzaSyBMfB2YS4eye4FNNWvyv71DV5HN3ld8GDs"
		#generate random placeTypes and append to requestLink
		requestLink = (requestLink + "&type=" + placeTypes[random.randint(0, len(placeTypes))])

		print(requestLink)
		
		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		print(placeResult)

		#pluck information from placeResult, open now?
		results = placeResult.get("results")

		print(results)

		for items in results:
			print(item["name"])

		#get place ID and get image, website

		return {
			"fulfillmentMessages": [
				{
					"text":{
						"text":[
							"Okay, here goes nothing!"
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
