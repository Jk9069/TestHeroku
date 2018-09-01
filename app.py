import urllib
import json
import os
import random

import weatherHandler
import weatherRecommendations

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
	if postedReq.get("action") == "weather":
		weatherInfo = weatherHandler.weatherResponse(postedReqParams, postedReq)
		return weatherInfo.getWeatherResponse()

	#user responded 'yes' to obtain place suggestions
	elif postedReq.get("action") == "GetWeather.GetWeather-yes":
		outputContexts = postedReq.get("outputContexts")
		weather = outputContexts[2].get("parameters").get("mainWeather")
		# for item in outputContexts:
		# 	parameters = item["parameters"]

		#obtained weather condition saved from prev intent, 
		#weather = outputContextsData['queryResult']['outputContexts'][2]['parameters']['mainW']
		print(weather)
		
		#based on weather condition, decide what kind of place to suggest
		weatherRecommend = weatherRecommendations.weatherPlaceRecommendations()
		return weatherRecommend.requestPlaces(weather)
					

#main
if __name__ == "__main__":
	port = int(os.getenv('PORT', 5000))
	#print ("Starting app on port %d" %(port))
	app.run(debug=True, port=port, host='0.0.0.0')

