import urllib
import json
import os
import random

from Place import Place

from flask import Flask
from flask import request
from flask import make_response

class purposePlaceQuery():

	def __init__(self, travelPurpose, latitude, longitude):
		self.travelPurpose = travelPurpose
		self.latitude = latitude
		self.longitude = longitude

	def requestPurposePlace(self):

		# ssearch when coordinates are provided 
		if self.latitude != None and self.longitude != None:
			requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI&rankby=distance&location="
			requestLink = requestLink + str(self.latitude) + ',' + str(self.longitude) + "&keyword=" + self.travelPurpose	
		else:
			requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&rankby=distance&key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI"
			requestLink = (requestLink + "&keyword=" + self.travelPurpose)

		print(requestLink)

		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		s = json.dumps(placeResult, indent=4, sort_keys = True)
		
		print (self.latitude)
		print(self.longitude)
		# print(s)
		
		return self.readnFormatResults(placeResult)

	#function to read and format json results
	def readnFormatResults(self, placeResult):
		responseText = ""
		shortlistPlaces = []
		data = {}

		#if there are results
		if (placeResult.get("status") == "OK"):
			#responseText = "Okay, showing " + categoryText 
			responseText = "Okay, here are some suggestions."

			#pluck information from placeResult
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

					#get types that categorise the place
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
				
			#googleLogo = Image.open("powered_by_google_on_white.png")
			data = {
				"source": "Google Places API", 
				"outputContexts": [
					{
						"name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/jk-travelPurpose-followup",
					    "lifespanCount": 2,
					    "parameters": {
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
							"card": { 
								 "title": place.getPlaceName(),
								 "subtitle": "Powered by Google",
								 "imageUri": "https://www.televox.com/webvox/wp-content/uploads/2015/09/9-8-15_1.png",
								 "buttons": [
								 	{
								 		"text": "Show Results",
								 		#link to open in google maps
								 		"postback": "https://www.google.com/maps/search/?api=1&query=" + self.travelPurpose
								 	}
								 ]
							}
						}
					)

			data["fulfillmentMessages"].append(
				{	
					"quickReplies": {
						"title": "What else can I help you with?",
						"quickReplies": [
							"Weather", "Events this week", "About Penang", "Bye!"
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
						"name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/jk-travelPurpose-followup",
					    "lifespanCount": 5,
					    "parameters": {
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




