import urllib
import json
import os
import random
import re

#Python Image Library
from PIL import Image 
from Place import Place
from emoji import UNICODE_EMOJI

from flask import Flask
from flask import request
from flask import make_response

class weatherPlaceRecommendations():

	def __init__(self, weather, latitude, longitude):
		self.weather = weather
		self.latitude = latitude
		self.longitude = longitude

	#from placeTypes search for places in Google Places API
	def requestPlaces(self):
		placeTypes = [
			'park', 'amusement_park', 'art_gallery',
			'bowling_alley', 'movie_theater', 'museum',
			'shopping_mall', 'spa', 'street_art', 'arcade',
			"restaurant", "cafe", "heritage", "lounge"
		]

		#remove outdoor places from recommendations
		if ('Rain' in self.weather or 'Thunderstorm' in self.weather):
			placeTypes.remove('park')
			placeTypes.remove('amusement_park')
			placeTypes.remove('street_art')
			placeTypes.remove('heritage')

		print(self.weather)

		# this one is to search penang when no coordinates provided
		# hardcode location of penang as 5.4356 (lat), 100.3091 (long)
		if self.latitude == None or self.longitude == None:
			requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&rankby=distance&key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI"
		else:
			#this one to search when coordinates are provided 
			requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI&rankby=distance&location="
			requestLink = requestLink + str(self.latitude) + ',' + str(self.longitude)	
		
		#both request links will need this
		#generate random placeTypes and append to requestLink
		randomCategory = placeTypes[random.randint(0, len(placeTypes)-1)]
		requestLink = (requestLink + "&type=" + randomCategory)

		print(requestLink)

		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		# s = json.dumps(placeResult, indent=4, sort_keys = True)
		# print(s)
		
		return self.readnFormatResults(placeResult, randomCategory)

	def readnFormatResults(self, placeResult, selectedCategory):
		responseText = ""
		shortlistPlaces = []
		data = {}

		contextCategory = selectedCategory

		if selectedCategory == 'library':
			selectedCategory = 'libraries'
		elif selectedCategory == 'art_gallery':
			selectedCategory = 'art galleries'
		else:
			selectedCategory = selectedCategory + 's'

		# already replaced in app.py
		# categoryText = selectedCategory.replace('_', ' ')
		# categoryText = selectedCategory.replace('%20', ' ')

		#if there are results
		if (placeResult.get("status") == "OK"):
			responseText = "Okay, showing " + selectedCategory.replace('_', ' ')

			#get place ID and get image, website
			results = placeResult.get("results")
			counter = 0;

			for items in results:
				if (counter < 7):
					if ("opening_hours" in items):
						openNow = items["opening_hours"].get("open_now")
						# print(openNow)
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
							else:
								photoRef = 'none'

						#using photo reference to get image
						if (photoRef != 'none'):
							photoRequest = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&key=AIzaSyBMfB2YS4eye4FNNWvyv71DV5HN3ld8GDs&photoreference=" + photoRef
							photoURL = urllib.request.urlopen(photoRequest).geturl()
							#print(photoURL)

						else:
							photoURL = "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png"
					else:
						photoRef = 'none'
						photoURL = "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png"

					# get type that categorise the places
					stringTypes = ""
					if ("types" in items):
						types = items["types"]

						for x in types:
							stringTypes += x + ", "

						#remove last 2 characters of the string
						stringTypes = stringTypes[:-2]
						
						if '_' in stringTypes:
							stringTypes = stringTypes.replace('_', " ")

					#create the Place object containing all required values
					newPlace = Place(placeID, placeName, rating, openNow, photoRef, photoURL, stringTypes)

					#add to array to be displayed
					shortlistPlaces.append(newPlace)
					counter += 1

				elif (counter == 7):
					stringTypes = []
		
					#create the Place object containing all required values
					newPlace = Place("-", "There are more results found on Google Maps!", "-", "-", "-", "-", stringTypes)

					#add to array to be displayed
					shortlistPlaces.append(newPlace)					
					counter += 1
				
				else:
					break
				
			if self.latitude == None or self.longitude == None:
				data = {
					"source": "Google Places API", 
					"outputContexts": [
						{
							"name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/GetWeather-recommend",
						    "lifespanCount": 2,
						    "parameters": {
						    	"prevCategory": contextCategory
						    }
						}
					],	
					"fulfillmentMessages":[
						{
							"text":{
								"text":[
									"Showing " + selectedCategory.replace('_', ' ') + " in George Town"
								]
							}
						}
					]
				}

			else:
				data = {
					"source": "Google Places API", 
					"outputContexts": [
						{
							"name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/GetWeather-recommend",
						    "lifespanCount": 5,
						    "parameters": {
						    	"prevCategory": contextCategory,
						    	"longitude": self.longitude,
						    	"latitude": self.latitude
						    }
						}
					],	
					"fulfillmentMessages":[
						{
							"text":{
								"text":[
									responseText
								]
							}
						}
					]
				}

			for x in range(len(shortlistPlaces)):
				place = shortlistPlaces[x]

				if (x < 7):
					data["fulfillmentMessages"].append(
						{
							# "platform": "FACEBOOK",
							"card": { 
								 "title": place.getPlaceName(),
								 "subtitle": place.getRating() + "\n" + place.getOpenNow() + "\n" + place.getPlaceTypes(), #+ "\n" + googleLogo.show(),
								 "imageUri": place.getPhotoURL(),
								 "buttons": [
								 	{
								 		"text": "Map",
								 		#link to open in google maps
								 		"postback": "https://www.google.com/maps/search/?api=1&query=" + place.getPlaceName() + "&query_place_id=" + place.getPlaceID()
								 	}
								 ]
							}
						}
					)
				elif (x == 7):
					data["fulfillmentMessages"].append(
						{
							# "platform": "FACEBOOK",
							"card": { 
								 "title": place.getPlaceName(),
								 "subtitle": "Powered by Google",
								 "imageUri": "https://www.televox.com/webvox/wp-content/uploads/2015/09/9-8-15_1.png",
								 "buttons": [
								 	{
								 		"text": "Show Results",
								 		#link to open in google maps
								 		"postback": "https://www.google.com/maps/search/?api=1&query=" + selectedCategory
								 	}
								 ]
							}
						}
					)

			# this section is for LINE platform
			lineData = {
				"payload": {
					"line":{
						"type": "template",
						"altText": "Results found.",
						"template": {
							"type": "carousel",
							"columns": [
								
							],
							
							"imageAspectRatio": "rectangle",
							"imageSize": "cover"
						}
					}
				}				
			}

			lineCarousel = lineData["payload"]["line"]["template"]["columns"]

			for x in range(len(shortlistPlaces)):
				place = shortlistPlaces[x]
				print("PLACE NAAMEE:" + place.getPlaceName())
				print(len(shortlistPlaces))

				if (x < 7):
					lineCarousel.append(
						{
							"thumbnailImageUrl": place.getPhotoURL(),
							"imageBackgroundColor": "#FFFFFF",
							"title": place.getPlaceName(),
							"text": place.getRating() + "\n" + place.getOpenNow(),
							"actions": [
								{
									"type": "uri",
									"label": "Map",
									"uri": "https://www.google.com/maps/search/?api=1&query=" + (place.getPlaceName()).replace(' ', '+') + "&query_place_id=" + place.getPlaceID()
								}
							]
						}
					)
				else:
					break					

			data["fulfillmentMessages"].append(lineData)

			if len(shortlistPlaces) > 7:
				data["fulfillmentMessages"].append(
					{
						"payload":{
							"line": {
								"type": "template",
								"altText": "More results found.",
								"thumbnailImageUrl": "https://example.com/bot/images/image.jpg",
								"imageAspectRatio": "rectangle",
								"imageSize": "cover",
								"template": {
									"type": "buttons",
									"imageBackgroundColor": "#FFFFFF",
									"title": "More results in Google Maps.",
									"text": "Powered by Google",
									"actions": [
										{
											"type": "uri",
											"label": "View results",
											"uri": "https://www.google.com/maps/search/?api=1&query=" + selectedCategory
										},
									]
								}
							}
						}
					}
				)

			#after showing results, ask if user want to change category
			data["fulfillmentMessages"].append(
				{	
					"quickReplies": {
						"title": "Not feeling like it? Let's choose other categories.",
						"quickReplies": [
							"Other category"
						]
					}					
				}
			)

		elif (placeResult.get("status") == "ZERO_RESULTS"):
			responseText = "No results found :("

			return {
				"fulfillmentText": responseText,
				"source": "Google Places API", 
				"outputContexts": [
					{
						"name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/GetWeather-recommend",
					    "lifespanCount": 5,
					    "parameters": {
					    	"prevCategory": contextCategory,
					    	"longitude": self.longitude,
					    	"latitude": self.latitude
					    }
					}
				]
			}

		elif (placeResult.get("status") == "OVER_QUERY_LIMIT"):
			responseText = "Over query limit. Please try again in a few moments"

			return {
				"fulfillmentText": responseText
			}

		else:
			responseText = "API Error encountered"

			return {
				"fulfillmentText": responseText
			}

		return data

	def requestMore(self, chosenCategory):
		#have to remove emojis before appending to the requestLink
		chosenCategory = self.remove_emoji(chosenCategory)
		chosenCategory = chosenCategory.lower()
		# chosenCategory = chosenCategory.replace('_', ' ')
		# chosenCategory = chosenCategory.replace('%20', ' ')
		
		#chosenCategory = self.remove_emoji(chosenCategory)
		print ("CHOSEN CATEGORY IS: " + chosenCategory)

		#just in case things get complicated and this happensx
		if chosenCategory == 'More':
			chosenCategory == 'points_of_interest'

		# this one is to search penang when no coordinates provided
		# hardcode location of george town as 5.4356 (lat), 100.3091 (long)
		if self.latitude == None or self.longitude == None:
			requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&rankby=distance&key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI"
		else:
			#this one to search when coordinates are provided 
			requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI&rankby=distance&location="
			requestLink = requestLink + str(self.latitude) + ',' + str(self.longitude)	
		
		requestLink = (requestLink + "&keyword=" + chosenCategory.replace(' ', '%20'))
		
		print(requestLink)
		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		# s = json.dumps(placeResult, indent=4, sort_keys = True)
		# print(s)
 
		return self.readnFormatResults(placeResult, chosenCategory)

	def remove_emoji(self, data):
		count = 0
		found = False
		
		for emoji in UNICODE_EMOJI:
			#count occurences of emoji
			count += data.count(emoji)
			if count >= 1:
				found = True
				break

		if found == True:
			data = data[2:]

		return data
