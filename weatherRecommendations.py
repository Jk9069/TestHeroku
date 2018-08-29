import urllib
import json
import os
import random

from flask import Flask
from flask import request
from flask import make_response

class weatherPlaceRecommendations():
	def __init__ (self, weather, placeTypes):
		self.weather = weather
		self.placeTypes = placeTypes

	def definePlaceTypes(self):
		#array that stores places that user can go on sunny weather
		self.placeTypes = [
			'zoo', 'park', 'amusement_park', 'aquarium', 'art_gallery',
			'bar', 'bowling_alley', 'cafe', 'department_store',
			'library', 'movie_theater', 'museum', 'night_club', 'restaurant',
			'shopping_mall', 'spa', 'points of interest', 'casino'
		]

		#remove outdoor places from recommendations
		if ('Rain' in self.weather or 'Thunderstorm' in self.weather):
			self.placeTypes.remove('zoo')
			self.placeTypes.remove('park')
			self.placeTypes.remove('amusement_park')


	#from placeTypes search for places in Google Places API
	def requestPlaces(self):
		placeNames = []

		#coordinates of penang: 5.285153 (lat), 100.456238 (long) - search Penang in general 
		requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&radius=15000&key=AIzaSyBMfB2YS4eye4FNNWvyv71DV5HN3ld8GDs"
		
		#generate random placeType and append to requestLink
		requestLink = requestLink + "&type=" + self.placeTypes[random.randint(0, len(self.placeTypes))]
		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#pluck information from placeResult, open now?
		results = placeResult.get("results")
		for items in results:
			placeNames.append(item["name"])

		#get place ID and get image, website

		return {
			"fulfillmentMessages": [
				{
					"text":{
						"text":[
							"Okay, here goes nothing!"
						]
					}
				},
				{
					"text": {
						"text": [
							placeNames[0]
						]
					}
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
				}
			],

			"source": 'Google Places API'
		}
