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


#def indoorOutdoor(mainWeather):

def getWebhookResult(postReq):
	postedReq = postReq.get("queryResult")
	postedReqParams = postReq.get("queryResult").get("parameters")
	fbPayload = postReq.get("originalDetectIntentRequest")

	#action / context will be used to determine what action is taken
	#user asks for weather
	#what about user location????
	if postedReq.get("action") == "weather":
		weatherInfo = weatherHandler.weatherResponse(postedReqParams, postedReq)
		return weatherInfo.getWeatherResponse()

	#user responded 'yes' to obtain place suggestions
	elif postedReq.get("action") == "GetWeather.GetWeather-yes" or postedReq.get("action") == "GetWeather.searchCategoryRecommendation":
		outputContexts = postedReq.get("outputContexts")
		latitude = fbPayload.get("coordinates").get("lat")
		longitude = fbPayload.get("coordinates").get("long")
		
		# for item in outputContexts:
		# 	if ("parameters" in item):
		# 		weather = item.get("parameters").get("mainWeather", 'empty')
		
		# #based on weather condition, decide what kind of place to suggest
		# weatherRecommend = weatherRecommendations.weatherPlaceRecommendations()

		# #if user asks for more, search based on text input, not type
		# if postedReq.get("action") == "GetWeather.searchCategoryRecommendation":
		# 	chosenCategory = postedReq.get("queryText")
		# 	print(chosenCategory)

		# 	#if user choose same as above, get prev intent category
		# 	for item in outputContexts:
		# 		if ("parameters" in item):
		# 			if ("prevCategory" in item.get("parameters")):
		# 				prevCategory = item.get("parameters").get("prevCategory")
		# 				print('outputContexts PREV CATEOGRY ' + prevCategory)

		# 	if prevCategory != None:
		# 		chosenCategory = remove_emoji(postedReq.get("queryText")).lower()
		# 		chosenCategory = chosenCategory.replace('%20', ' ')
		# 		chosenCategory = chosenCategory.replace('_', ' ')
		# 		#print('NOT NONE' + chosenCategory)
				
		# 		if 'same as above' in chosenCategory or 'same' in chosenCategory: 
		# 			chosenCategory = prevCategory

		# 	#print(chosenCategory)
		# 	x = weatherRecommend.requestMore(chosenCategory)
		# else: 
		# 	#default get place recommendation, search based on type
		# 	x = weatherRecommend.requestPlaces(weather)


		# return x
		return {
			"fulfillmentMessages": [
				{
					"text":{
						"text":[
							"latitude is " + latitude
						]
					}
				},
				{
					"text": {
						"text":[
							"longitude is " + longitude
						]
					}
				}
			]
		}

	#what happens after show places after recommendation????
	elif postedReq.get('action') == "getTravelPurpose":
		purpose = postedReqParams.get('purpose')

		placeRecommend = purposePlaceQuery.purposePlaceQuery(purpose)
		return placeRecommend.requestPurposePlace()

		# return {
		# 	"fulfillmentMessages": [
		# 		{
		# 			"text":{
		# 				"text":[
		# 					"Your purpose is " + purpose
		# 				]
		# 			}
		# 		}
		# 	]
		# }

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
			# 	# 			"subtitle": rating? address?,
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

