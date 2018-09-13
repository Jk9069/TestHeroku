import urllib
import json
import os
import random
import re

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
		randomCategory = placeTypes[random.randint(0, len(placeTypes)-1)]
		requestLink = (requestLink + "&type=" + randomCategory)

		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		s = json.dumps(placeResult, indent=4, sort_keys = True)
		print(requestLink)
		print(s)
		
		return self.readnFormatResults(placeResult, randomCategory)

	def readnFormatResults(self, placeResult, selectedCategory):
		responseText = ""
		shortlistPlaces = []
		data = {}

		categoryText = selectedCategory.replace('_', ' ')
		categoryText = selectedCategory.replace('%20', ' ')
		if categoryText == 'library':
			categoryText = 'libraries'
		elif categoryText == 'art_gallery':
			categoryText = 'art_galleries'
		else:
			categoryText = categoryText + 's'

		#if there are results
		if (placeResult.get("status") == "OK"):
			responseText = "Okay, showing " + categoryText 

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
						else:
							photoRef = 'none'

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
						stringTypes += x + ", "

					#remove last 2 characters of the string
					stringTypes = stringTypes[:-2]
					
					if '_' in stringTypes:
						stringTypes = stringTypes.replace('_', " ")

				#create the Place object containing all required values
				newPlace = Place(placeID, placeName, rating, openNow, photoRef, photoURL, stringTypes)

				#add to array to be displayed
				if (counter < 10):
					shortlistPlaces.append(newPlace)
					counter += 1
				else:
					break
				
			#googleLogo = Image.open("powered_by_google_on_white.png")
			data = {
				"source": "Google Places API", 
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
							 		"text": "Map",
							 		#link to open in google maps
							 		"postback": "https://www.google.com/maps/search/?api=1&query=" + place.getPlaceName() + "&query_place_id=" + place.getPlaceID()
							 	}
							 ]
						}
					}
				)

		elif (placeResult.get("status") == "ZERO_RESULTS"):
			responseText = "No results found :("

			return {
				"fulfillmentText": responseText
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
		chosenCategory = chosenCategory.replace(' ', '%20')
		#remove_emoji works but isnt removing first 2 chars easier? ._.
		#chosenCategory = self.remove_emoji(chosenCategory)
		print ("CHOSEN CATEGORY IS: " + chosenCategory)

		#just in case things get complicated and this happensx
		if chosenCategory == 'More':
			chosenCategory == 'points_of_interest'

		#initiate search using keyword from nearby search
		requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&radius=15000&key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI"
		requestLink = (requestLink + "&keyword=" + chosenCategory)

		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		s = json.dumps(placeResult, indent=4, sort_keys = True)
		print(requestLink)
		print(s)
 
		return self.readnFormatResults(placeResult, chosenCategory)

	def remove_emoji(self, data):
		emoji_pattern = re.compile(
			"["
			u"\U0001F600-\U0001F64F"  # emoticons
			u"\U0001F300-\U0001F5FF"  # symbols & pictographs
			u"\U0001F680-\U0001F6FF"  # transport & map symbols
			u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
			"]+", flags=re.UNICODE
		)

		text = emoji_pattern.sub(r'', data)
		
		if (text[0] == ' '):
			text = text[1:]

		return text
