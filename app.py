import urllib
import json
import os
import random

import weatherHandler
import weatherRecommendations
import purposePlaceQuery

from flask import Flask
from flask import request
from flask import make_response

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

	#action / context will be used to determine what action is taken
	#user asks for weather
	#what about user location????
	if postedReq.get("action") == "weather":
		weatherInfo = weatherHandler.weatherResponse(postedReqParams, postedReq)
		return weatherInfo.getWeatherResponse()

	#user responded 'yes' to obtain place suggestions
	elif postedReq.get("action") == "GetWeather.GetWeather-yes" or postedReq.get("action") == "GetWeather.searchCategoryRecommendation":
		outputContexts = postedReq.get("outputContexts")
		
		for item in outputContexts:
			if ("parameters" in item):
				weather = item.get("parameters").get("mainWeather", 'empty')
		
		#based on weather condition, decide what kind of place to suggest
		weatherRecommend = weatherRecommendations.weatherPlaceRecommendations()

		#if user asks for more, search based on text input, not type
		if postedReq.get("action") == "GetWeather.searchCategoryRecommendation":
			chosenCategory = postedReq.get("queryText")
			print(chosenCategory)
			#if user choose same as above, have to get prev intent category
			for item in outputContexts:
				if ("parameters" in item):
					prevCategory = item.get("parameters").get("prevCategory", 'empty')
					print(prevCategory)

			if prevCategory != 'empty':
				chosenCategory = remove_emoji(postedReq.get("queryText")).lower()
				
				if 'same as above' in chosenCategory or 'same' in chosenCategory: 
					chosenCategory = prevCategory

			print(chosenCategory)
			x = weatherRecommend.requestMore(chosenCategory)
		else: 
			#default get place recommendation, search based on type
			x = weatherRecommend.requestPlaces(weather)


		return x

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

