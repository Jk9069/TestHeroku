import urllib
import json
import os
import random
import re

import weatherHandler
import weatherRecommendations
import purposePlaceQuery

from flask import Flask
from flask import request
from flask import make_response
from emoji import UNICODE_EMOJI

#global var 
app = Flask(__name__);

#routes the app to webhook function
@app.route('/WeatherWebhook', methods=['POST'])

def WeatherWebhook():
	#get post request
	postReq = request.get_json(silent=True, force=True)

	#prints out the post request (viewing purposes only)
	print("Request:\n");
	print(json.dumps(postReq, indent=4))

	#pass the post request to another function to obtain a result from API
	apiResult = getWebhookResult(postReq)

	#print out result (viewing purposes only)
	apiResult = json.dumps(apiResult, indent=4)
	print(apiResult)

	#return result to chatbot to respond to user
	finResult = make_response(apiResult)
	finResult.headers['Content_Type'] = 'application/json'
	return finResult

def getWebhookResult(postReq):
	postedReq = postReq.get("queryResult")
	postedReqParams = postReq.get("queryResult").get("parameters")
	outputContexts = postedReq.get("outputContexts")

	#action / context will be used to determine what action is taken
	#user asks for weather
	if postedReq.get("action") == "weather":
		weatherInfo = weatherHandler.weatherResponse(postedReqParams, postedReq)
		return weatherInfo.getWeatherResponse()

	#user responded 'yes' to obtain place suggestions
	elif postedReq.get("action") == "GetWeather.GetWeather-yes" or postedReq.get("action") == "GetWeather.searchCategoryRecommendation":
		fbPayload = postReq.get("originalDetectIntentRequest").get("payload").get("data").get("postback")

		#get weather condition
		for item in outputContexts:
			if ("parameters" in item):
				weather = item.get("parameters").get("mainWeather", 'empty')

		#if action is GetWeather.GetWeather-yes, get location from facebook payload
		# and then perform search
		if postedReq.get("action") == "GetWeather.GetWeather-yes":
			latitude = fbPayload.get("data").get("lat")
			longitude = fbPayload.get("data").get("long")

			#default get place recommendation, search based on type
			#based on weather condition, decide what kind of place to suggest
			weatherRecommend = weatherRecommendations.weatherPlaceRecommendations(weather, latitude, longitude)
			x = weatherRecommend.requestPlaces()

		#if not, get location from output contexts
		#and then perform search 
		elif postedReq.get("action") == "GetWeather.searchCategoryRecommendation":
			#get latitude, longitude and previous category from outputContexts
			for item in outputContexts:
				if ("parameters" in item):
					if ("latitude" in item.get("parameters") and "longitude" in item.get("parameters")):
						latitude = item.get("parameters").get("latitude")
						longitude = item.get("parameters").get("longitude")
						print ("searchCategoryRecommendation LATITUDE: " + str(latitude))
						print ("searchCategoryRecommendation longitude: " + str(longitude))
					else:
						latitude = None
						longitude = None

					#if user choose same as above, get prev intent category
					if ("prevCategory" in item.get("parameters")):
						prevCategory = item.get("parameters").get("prevCategory")
						print('outputContexts PREV CATEOGRY ' + prevCategory)
					else:
						prevCategory = None
		
			#get chosen category (can be either same or new category)
			chosenCategory = postedReq.get("queryText")
			print(chosenCategory)

			if prevCategory != None:
				chosenCategory = remove_emoji(postedReq.get("queryText")).lower()
				chosenCategory = chosenCategory.replace('%20', ' ')
				chosenCategory = chosenCategory.replace('_', ' ')
				#print('NOT NONE' + chosenCategory)
				
				if 'same as above' in chosenCategory or 'same' in chosenCategory: 
					chosenCategory = prevCategory

			#print(chosenCategory)
			#based on weather condition, decide what kind of place to suggest
			weatherRecommend = weatherRecommendations.weatherPlaceRecommendations(weather, latitude, longitude)
			x = weatherRecommend.requestMore(chosenCategory)

		return x

	#what happens after show places after recommendation????
	elif postedReq.get('action') == "jk-travelPurpose.jk-travelPurpose-coordinateSearch" or postedReq.get('action') == "jk-travelPurpose-placeCategory-getResult":
		fbPayload = postReq.get("originalDetectIntentRequest").get("payload").get("data").get("postback")

		latitude = fbPayload.get("data").get("lat")
		longitude = fbPayload.get("data").get("long")
		
		if postedReq.get('action') == "jk-travelPurpose.jk-travelPurpose-coordinateSearch":
			for item in outputContexts:
				if ("parameters" in item):
					if ("purpose.original" in item.get("parameters")):
						purpose = item.get("parameters").get("purpose.original")

		elif postedReq.get('action') == "jk-travelPurpose-placeCategory-getResult":
			for item in outputContexts:
				if ("parameters" in item):
					if ("placeCategory.original" in item.get("parameters")):
						purpose = item.get("parameters").get("placeCategory.original")

		placeRecommend = purposePlaceQuery.purposePlaceQuery(purpose.replace(' ', '%20'), latitude, longitude)
		return placeRecommend.requestPurposePlace()

	elif postedReq.get('action') == "getEvent":
		categories = [
			"learning_education", "music", "science", 
			"business", "support", "outdoors_recreation", 
			"performing_arts", "religion_spirituality",
			"miscellaneous"
		]

		requestLink = "http://api.eventful.com/json/events/search?app_key=ccLj6sppM4RsQ4wX&location=George%20town,Pulau%20Pinang"

		# search for event or concert, depending on user input
		if ("eventConcert" in postedReqParams):
			searchEvent = postedReqParams.get("eventConcert")

			# get the time period or date to search
			if ("date-period" in postedReqParams):
				if (postedReqParams.get("date-period") != ""):
					startDate = postedReqParams.get("startDate")
					startDate = (startDate[:10]).replace('-', '') + '00'
					endDate = postedReqParams.get("endDate")
					endDate = (endDate[:10]).replace('-', '') + '00'

					requestLink = requestLink + "&date=" + str(startDate) + "-" + str(endDate)
				
			elif ("date" in postedReqParams):
				if postedReqParams.get("date") != "":
					date = postedReqParams.get("date")
					date = (date[:10]).replace('-', '')+ "00"

					requestLink = requestLink + "&date=" + str(date) + "-" + str(date)

			#start search here, searh with no categories first
			#requestLink = requestLink + "&category=" + "???"

		return {
			"fulfillmentText": requestLink
		}

	# elif postedReq.get('action') == "PenangInfo":
					
def remove_emoji(data):
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


#main
if __name__ == "__main__":
	port = int(os.getenv('PORT', 5000))
	#print ("Starting app on port %d" %(port))
	app.run(debug=True, port=port, host='0.0.0.0')


	# "fulfillmentMessages": [
			# 	{
			# 		"text":{
			# 			"text":[
			# 				responseText
			# 			]
			# 		}
			# 	},

			# 	# {
			# 	# 	"card": {
			# 	# 			"title": "name",
			# 	# 			"subtitle": rating/address,
			# 	# 			"imageUri": "image"
			# 	# 			"buttons": [
			# 	# 				{
			# 	# 					"text": "More details",
			# 	# 					"postback": "url "
			# 	# 				}
			# 	# 			]
			# 	# 		}
			# 	# }
			# ]

