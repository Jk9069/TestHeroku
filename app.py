import urllib
import json
import os
import random
import re

import weatherHandler
import weatherRecommendations
import purposePlaceQuery
import eventFinder

from food import Food
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
	elif postedReq.get("action") == "GetWeather.GetWeather-yes" or postedReq.get("action") == "GetWeather.searchCategoryRecommendation" or postedReq.get("action") == "GetWeather.GetWeather-yesLocation.GeneralSearch":
		#get weather condition
		for item in outputContexts:
			if ("parameters" in item):
				weather = item.get("parameters").get("mainWeather", 'empty')

		#if action is GetWeather.GetWeather-yes, get location from facebook payload
		# and then perform search
		if postedReq.get("action") == "GetWeather.GetWeather-yes":
			fbPayload = postReq.get("originalDetectIntentRequest").get("payload").get("data").get("postback")
			latitude = fbPayload.get("data").get("lat")
			longitude = fbPayload.get("data").get("long")

			#default get place recommendation, search based on type
			#based on weather condition, decide what kind of place to suggest
			weatherRecommend = weatherRecommendations.weatherPlaceRecommendations(weather, latitude, longitude)
			x = weatherRecommend.requestPlaces()

		#if no facebook location, get location from output contexts
		#and then perform search 
		elif postedReq.get("action") == "GetWeather.searchCategoryRecommendation":
			# initialise
			latitude = ""
			longitude = ""

			#get latitude, longitude and previous category from outputContexts
			for item in outputContexts:
				if ("parameters" in item):
					if ("latitude" in item.get("parameters") and "longitude" in item.get("parameters")):
						latitude = item.get("parameters").get("latitude", "")
						longitude = item.get("parameters").get("longitude", "")
						print ("searchCategoryRecommendation LATITUDE: " + str(latitude))
						print ("searchCategoryRecommendation longitude: " + str(longitude))

					#if user choose same as above, get prev intent category
					# if ("prevCategory" in item.get("parameters")):
					# 	prevCategory = item.get("parameters").get("prevCategory")
					# 	print('outputContexts PREV CATEOGRY ' + prevCategory)
					# 	break
		
			#get chosen category (can be either same or new category)
			# chosenCategory = postedReq.get("queryText")

			# if prevCategory != None:
			chosenCategory = remove_emoji(postedReq.get("queryText")).lower()
			print(chosenCategory)
	
			# if 'same as above' in chosenCategory or 'same' in chosenCategory.split() or 'above' in chosenCategory.split(): 
			# 	chosenCategory = prevCategory
			
			chosenCategory = chosenCategory.replace('%20', ' ')
			chosenCategory = chosenCategory.replace('_', ' ')

			# print(chosenCategory)
			# in the case chatbot could not get location from outputContexts and facebook location
			# set to None first, later will check if none then search only in george town penang
			if latitude == "" and longitude == "":
				latitude = None
				longitude = None
				
			#based on weather condition, decide what kind of place to suggest
			weatherRecommend = weatherRecommendations.weatherPlaceRecommendations(weather, latitude, longitude)
			x = weatherRecommend.requestMore(chosenCategory)

		# for search in george town only	
		elif postedReq.get("action") == "GetWeather.GetWeather-yesLocation.GeneralSearch":
			latitude = None
			longitude = None

			weatherRecommend = weatherRecommendations.weatherPlaceRecommendations(weather, latitude, longitude)
			x = weatherRecommend.requestPlaces()


		return x

	# handles user search based on their purpose (have user coordinates)
	elif postedReq.get('action') == "jk-travelPurpose.jk-travelPurpose-coordinateSearch" or postedReq.get('action') == "jk-travelPurpose-placeCategory-getResult":
		# get facebook location
		fbPayload = postReq.get("originalDetectIntentRequest").get("payload").get("data").get("postback")
		latitude = fbPayload.get("data").get("lat")
		longitude = fbPayload.get("data").get("long")

		# if user search based on customized term
		if postedReq.get('action') == "jk-travelPurpose.jk-travelPurpose-coordinateSearch":
			for item in outputContexts:
				if ("parameters" in item):
					if ("purpose.original" in item.get("parameters")):
						purpose = item.get("parameters").get("purpose.original")

		# if user search based on a place category
		elif postedReq.get('action') == "jk-travelPurpose-placeCategory-getResult":
			for item in outputContexts:
				if ("parameters" in item):
					if ("placeCategory.original" in item.get("parameters")):
						purpose = item.get("parameters").get("placeCategory.original")

		# perform search
		placeRecommend = purposePlaceQuery.purposePlaceQuery(purpose.replace(' ', '%20'), latitude, longitude)
		return placeRecommend.requestPurposePlace()

	# handles search only in george town (when dont have user coordinates)
	elif postedReq.get("action") == "jk-travelPurpose.jk-travelPurpose-generalSearch" or postedReq.get("action") == "jk-travelPurpose-placeCategory-GeneralSearch":
		# if user search based on customized term
		if postedReq.get('action') == "jk-travelPurpose.jk-travelPurpose-generalSearch":
			for item in outputContexts:
				if ("parameters" in item):
					if ("purpose.original" in item.get("parameters")):
						purpose = item.get("parameters").get("purpose.original")

		# if user search based on a place category
		elif postedReq.get('action') == "jk-travelPurpose-placeCategory-GeneralSearch":
			for item in outputContexts:
				if ("parameters" in item):
					if ("placeCategory.original" in item.get("parameters")):
						purpose = item.get("parameters").get("placeCategory.original")

		# since no coordinates, perform search without latitude and longitude data
		latitude = None
		longitude = None
		placeRecommend = purposePlaceQuery.purposePlaceQuery(purpose.replace(' ', '%20'), latitude, longitude)
		
		return placeRecommend.requestPurposePlace()

	#if user asks for events
	elif postedReq.get('action') == "getEvent":
		# search for event from user input
		eventLookup = eventFinder.eventFinder(postedReqParams)
		return eventLookup.performSearch()

	#handle info about penang
	#show best foods
	elif postedReq.get('action') == "jk-PenangInfo.jk-PenangInfo-bestfoods":
		# provide 3 sets of best foods, will take randomized results from each
		# more to snacks category
		foodSet1 = [
			"Apom Balik", 
			"Roti Canai", "Roti Tisu",
			"Popiah", "Satay",
			"Fried Oyster", "Pasembur",
			"Lor Bak", "Char Koay Kak"
		]

		set1Desc = [
			"Pancake. Dessert. Peanuts.",
			"Flatbread. Breakfast. Snack.",
			"Flatbread. Sweet. Thin like tissue.",
			"Teochew-style spring roll.",
			"Seasoned, skewered, grilled meat.",
			"Omelette filled with small oysters.",
			"Malaysian Indian salad.", 
			"Mixed plate of deep fried snacks.",
			"Fried rice cakes."
		]

		# more to main meal category
		foodSet2 = [
			"Char Koay Teow", "Curry Mee",
			"Penang Hokkien Mee", "Mee Goreng",
			"Lok Lok", "Penang Assam Laksa", 
			"Nasi Kandar", "Char Hor Fun",
			"Koay Teow Soup", "Wanton Mee",
			"Lor Mee", "Nasi Lemak"
		]

		set2Desc = [
			"Fried. Flat rice noodles. Best.",
			"Noodles and/or rice vermicelli in spicy curry soup.",
			"Spicy prawn broth with noodles and/or rice vermicelli.",
			"Fried Indian noodles. Spicy.",
			"Various foods such as meat and vegetables served on a skewer.",
			"Sour. Thick rice noodles in fish and tamarind-based soup.",
			"Steamed rice served with a variety of curries and side dishes.",
			"Fried broad rice noodles in treacly gravy.",
			"Flat rice noodles in warm soup.",
			"Noodle dish served in either soup or dry soy sauce.",
			"Noodle and vermicelli served in thick soy sauce gravy.",
			"Malay fragrant rice dish. Spicy. Best."
		]

		# more to desserts category
		foodSet3 = [
			"Penang Teochew Cendol", "Ice Kacang",
			"Rojak", "Nyonya Kuih", 
			"Muar Chee", "Coconut Shake",
			"Putu Mayam", "Coconut Jelly",
			"Aiyu Jelly/Oh Kio", "Ais Tingkap/Window Sherbet"
		]

		set3Desc = [
			"Iced, sweet dessert. Green rice flour jelly. Coconut milk.",
			"Shaved ice. Dessert. Topped with various toppings.",
			"Fruit and vegetable salad mixed with prawn paste.",
			"Wide spectrum of colorful desserts. Unique taste and shape.",
			"Steamed glutinous flour dough coated with fine sugar and crushed peanuts.",
			"Blended coconut drink topped with coconut ice cream and chewy pearls.",
			"Indian style steamed rice vermicelli cake served with sugar and grated coconut.",
			"Sweet. Cooling dessert. Coconut flavored jelly.",
			"Taiwan traditional dessert. Jelly with lemonade, sugar and lychee.",
			"Coconut water in red syrup. Topped with basil seeds and coconut flesh."
		]

		shortlistedFoods = []

		# add items into the array list using randomizer
		for x in range(0, 8):
			#if counter is less than 4 take 3 items from set 1
			if (len(shortlistedFoods) < 4):
				randomInt = random.randint(0, (len(foodSet1) - 1))
				foodItem = food.Food(foodSet1[randint], set1Desc[randint])

			#if counter is less than 7, take another 3 items from set 2
			elif (len(shortlistedFoods) < 7):
				randomInt = random.randint(0, (len(foodSet2) - 1))
				foodItem = food.Food(foodSet2[randint], set2Desc[randint])

			#for the remaining loops, take items from set 3	
			else:
				randomInt = random.randint(0, (len(foodSet3) - 1))
				foodItem = food.Food(foodSet3[randint], set3Desc[randint])

			print(foodItem.getFoodName())
			shortlistedFoods.append(foodItem)


		# format data to be returned
		data = {
			"fulfillmentMessages":[
				{
					"text":{
						"text":[
							"These are some of the best foods in Penang."
						]
					}
				}
			]
		}

		for x in range(len(shortlistedFoods)):
			foods = shortlistedFoods[x]

			data["fulfillmentMessages"].append(
				{
					"card": { 
						 "title": foods.getFoodName(),
						 "subtitle": foods.getFoodDesc(),
						 "imageUri": "https://sethlui.com/wp-content/uploads/2015/06/penang-street-hawker-food.jpg",
						 "buttons": [
						 	{
						 		"text": "Find where",
						 		#link to open in google maps
						 		"postback": "https://www.google.com/maps/search/?api=1&query=" + foods.getFoodName()
						 	}
						 ]
					}
				}
			)

		return data
					
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

