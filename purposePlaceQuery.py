import urllib
import json
import os
import random

from Place import Place

from flask import Flask
from flask import request
from flask import make_response

class purposePlaceQuery():

	def __init__(self, travelPurpose):
		self.travelPurpose = travelPurpose

	def requestPurposePlace():
		#search based on what purpose user enters
		#user location ????
		requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&radius=15000&key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI"
		requestLink = (requestLink + "&keyword=" + self.travelPurpose)

		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		s = json.dumps(placeResult, indent=4, sort_keys = True)
		print(requestLink)
		print(s)
		
		results = placeResult.get("results")
		counter = 0;
		listPlaceNames = []

		for items in results:
			placeName = items["name"]
			listPlaceNames.append(placeName)
			counter += 1

			if counter > 9:
				break;

		return {
			"fulfillmentText": "This is optional",
			"fulfillmentMessages": [
				{
					"text": {
						"text": [
							listPlaceNames[0]
						]
					}
				},
				{
					"text": {
						"text": [
							listPlaceNames[1]
						]
					}
				},
				{
					"text": {
						"text": [
							listPlaceNames[2]
						]
					}
				}
			],
			"source": "Google Places API"
		}

	#function to read and format json results? 
