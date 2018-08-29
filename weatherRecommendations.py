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

	def __init__ (self, postedReq):
		self.postedReq = postedReq

		outputContexts = self.postedReq.get("queryResult").get("outputContexts")
		for item in outputContexts:
			parameters = item["parameters"]

		#obtained weather condition saved from prev intent, 
		#based on weather condition, decide what kind of place to suggest
		self.weather = parameters.get("mainWeather")

		#remove outdoor places from recommendations
		if ('Rain' in self.weather or 'Thunderstorm' in self.weather):
			self.placeTypes.remove('zoo')
			self.placeTypes.remove('park')
			self.placeTypes.remove('amusement_park')

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
