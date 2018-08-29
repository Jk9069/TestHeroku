import urllib
import json
import os
import random

from flask import Flask
from flask import request
from flask import make_response

class weatherPlaceRecommendations():
	#array that stores places that user can go on sunny weather
	placeTypes = [
		'zoo', 'park', 'amusement_park', 'aquarium', 'art_gallery',
		'bar', 'bowling_alley', 'cafe', 'department_store',
		'library', 'movie_theater', 'museum', 'night_club', 'restaurant',
		'shopping_mall', 'spa', 'points of interest', 'casino'
	]

	def __init__ (self, weather):
		global placeTypes
		self.weather = weather

		#remove outdoor places from recommendations
		if ('Rain' in self.weather or 'Thunderstorm' in self.weather):
			placeTypes.remove('zoo')
			placeTypes.remove('park')
			placeTypes.remove('amusement_park')

	#from placeTypes search for places in Google Places API
	def requestPlaces(self):

		return {
			"fulfillmentMessages": [
				{
					"text":{
						"text":[
							"Okay, here goes nothing!"
						]
					}
				}
				#},
				# {
				# 	"text":{
				# 		"text": [
				# 			"Let me access your location"
				# 		]
				# 	}
				# }
			],

			"source": 'Google Places API'
		}
