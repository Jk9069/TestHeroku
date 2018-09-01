import urllib
import json
import os
import random

from flask import Flask
from flask import request
from flask import make_response

class weatherPlaceRecommendations():

	#from placeCategory search for places in Google Places API
	def requestPlaces(self, weather):
		stayIndoor = False

		#categories and tags
		placeCategory = [
			'discovering', 'eating', 'going_out', 'hiking',
			'playing', 'relaxing', 'shopping', 'sightseeing',
			'doing_sports', 'traveling'			
		]

		# placeTags = [
		# 	''

		# ]

		if ('Rain' in weather or 'Thunderstorm' in weather):
			#append indoor tag?
			stayIndoor = True


		#generate random placeCategory and append to requestLink
		requestLink = "https://api.sygictravelapi.com/1.0/en/places/list?parents=city:3350&bounds=5.237559,100.347503,5.479325,100.173052&limit=20"

		#"level=poi&"
		#get random place category 
		requestLink = requestLink + "&categories=" + placeCategory[random.randint(0, len(placeCategory))]

		if (stayIndoor == True):
			requestLink = requestLink + "&tags=indoor"

		#so that can view actual results on web browser
		print(requestLink)
	
		#post url, with headers for sygic travel api key
		request = urllib.request.Request(requestLink, headers={'x-api-key':'MbSr78YZnbagZpgKINcfb16CcksWk7zyIF8FMzm5'})
		placeResult = (urllib.request.urlopen(request)).read()

		print(placeResult)

		#if there are results
		responseText = ""
		if (placeResult.get("status_code") == 200):
			responseText = "Okay, here goes nothing!"

			#pluck information from placeResult, open now?
			results = placeResult.get("data").get("places")

			for items in results:
				print(item["name"])

		#what about when no results found?
		else:
			responseText = "No results found :("


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
