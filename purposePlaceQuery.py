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
		#coordinates of penang: 5.4356 (lat), 100.3091 (long) - search Penang in general 
		#generate random placeTypes and append to requestLink
		requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=5.4356,100.3091&radius=15000&key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI"
		
		#based on text append to request link to search
		requestLink = (requestLink + "&type=" + randomCategory)

		#post url
		placeResult = json.loads(urllib.request.urlopen(requestLink).read())

		#for viewing purposes in logs only
		s = json.dumps(placeResult, indent=4, sort_keys = True)
		print(requestLink)
		print(s)
		
		return self.readnFormatResults(placeResult, randomCategory)
