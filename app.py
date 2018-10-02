import urllib
import json
import os
import random
import re

import weatherHandler
import weatherRecommendations
import purposePlaceQuery
import eventFinder

from Food import Food
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

		set1Img = [
			"https://thumbor.thedailymeal.com/SwjjdmBW7aT67LpGKfcSGGvzXyw=/840x565/https://www.thedailymeal.com/sites/default/files/2016/01/13/SSWF-ApamBalik.JPG",
			"https://www.rotinrice.com/wp-content/uploads/2011/04/RotiCanai-1.jpg",
			"https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/RotiTissue001.jpg/250px-RotiTissue001.jpg",
			"http://apcdn.ar-cdn.com/recipes/port500/8dbe4282-5bfc-432a-bd01-b43d7a9333ec.jpg",
			"https://www.irishtimes.com/polopoly_fs/1.2854640.1478261927!/image/image.jpg_gen/derivatives/landscape_620/image.jpg",
			"http://lh5.ggpht.com/7nCmsOVON1KhAd64TsSme8L-YS2UsTEO_t4YeTw_CFnHgCDdRco82sunQsO9UJHECJf35tVwVvGpZp3p6AEQF1A0LA=s800",
			"https://enqvistlim.files.wordpress.com/2016/10/kareempasembu-10.jpg",
			"https://www.chowstatic.com/uploads/4/9/6/827694_dscn4343.jpg",
			"http://www.penangtrails.com.my/wp-content/uploads/2016/07/Char-Koay-Kak.jpg"
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

		set2Img = [
			"https://iluminasi.com/img/thumb/banner-resepi-char-koay-teow-power-5394.jpg",
			"https://farm5.staticflickr.com/4347/35556167003_d39b2b8ef9_o.jpg",
			"https://cdn-geo.dayre.me/tfss-9d709c46-c7a2-4907-baa9-2966cd61800f-jzSCpkB6SC9gGrwCd46Y.jpg",
			"https://img.delicious.com.au/5RBEZeCF/h506-w759-cfill/del/2017/07/malaysian-chicken-mee-goreng-49049-2.jpg",
			"https://4.bp.blogspot.com/-iBYEPz00EtM/V57ng5IkqsI/AAAAAAAAnOA/u7sJRie0NZsKBoRrK04AnSvJ7gv_VQRZwCLcB/s640/1-IMG_3606.jpg",
			"http://3.bp.blogspot.com/-GjfaSKMCMKs/Tnf51by8-MI/AAAAAAAACZY/6JcsB62LeXQ/s1600/Penang+asam+laksa.JPG",
			"https://www.thestar.com.my/~/media/online/2015/05/08/21/20/metd_0905_25chosfa_kkeeran_1.ashx/?w=620&h=413&crop=1&hash=24E9A0DBA679F1E75737D0B98DCD936FE0FC9C29",
			"http://2.bp.blogspot.com/_AtmigDQCfxk/S953qbG0vaI/AAAAAAAAAJM/2J00bDI3U2I/s1600/hor+fun.JPG",
			"https://www.rotinrice.com/wp-content/uploads/2013/11/IMG_3364.jpg",
			"https://rasamalaysia.com/wp-content/uploads/2012/07/wontonnoodles_thumb.jpg",
			"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1uS9W-Y5szflWE0QoeHqSkWPesxxEM4jSVKUaw8oZ9hYThupZ",
			"http://images.tastespotting.com/uploads/thumbnail/270202.jpg"
		]

		set2Desc = [
			"Fried. Flat rice noodles. Best.",
			"Noodles. Rice vermicelli. Spicy curry soup.",
			"Spicy prawn broth with noodles and/or rice vermicelli.",
			"Fried Indian noodles. Spicy.",
			"Various foods served on a skewer.",
			"Sour. Thick rice noodles in fish and tamarind-based soup.",
			"Rice served with a variety of curries and side dishes.",
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

		set3Img = [
			"https://i.ytimg.com/vi/ECVpD3gLF3I/maxresdefault.jpg",
			"https://previews.123rf.com/images/spukkato/spukkato1803/spukkato180300314/97666983-soft-focus-of-ais-kacang-topped-with-basil-seeds-peanuts-corn-and-a-scoop-of-ice-cream-ice-kacang-li.jpg",
			"https://www.bbcgoodfood.com/sites/default/files/styles/recipe/public/recipe/recipe-image/2017/08/rojak.jpg?itok=y8XZJMoN",
			"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR5J0OqgXMelEizozaGc7dnfImxP9gG4wSYY5YsWqubbkjR75yX",
			"https://aforchinese.files.wordpress.com/2016/03/muah-chee.jpg",
			"https://fa-assets-production.cdnedge.bluemix.net/attachments/695435f511d9b1eaf071fd1d44bfa3a8c040e09f/store/fill/800/500/5317331a2610c43393a259ea9c24186fd6d06b878eb30d472e2458e2fe26/featured_image.jpg",
			"https://uf.cari.com.my/forumx/mforum/portal/201802/07/210210l5lcpbclcnizmyci.jpg",
			"http://bagus.com.my.ws8.webshaper.com.my/webshaper/pcm/pictures/coconut%20jelly%202.jpg",
			"https://igx.4sqi.net/img/general/200x200/wMTal50L9gQdPVMg65R7SZD7tl8I1l5ytNPau6QCe04.jpg",
			"https://media.timeout.com/images/101703185/630/472/image.jpg"
		]

		set3Desc = [
			"Iced, sweet dessert. Green rice flour jelly. Coconut milk.",
			"Shaved ice. Dessert. Topped with various toppings.",
			"Fruit and vegetable salad mixed with prawn paste.",
			"Wide spectrum of colorful desserts. Unique taste and shape.",
			"Steamed glutinous flour dough. Sugar. Crushed peanuts.",
			"Blended. Topped with coconut ice cream and chewy pearls.",
			"Steamed rice vermicelli cake. Sugar. Grated coconut.",
			"Sweet. Cooling dessert. Coconut flavored jelly.",
			"Taiwan traditional dessert. Jelly with lemonade and sugar.",
			"Coconut water in red syrup. Basil seeds. Coconut flesh."
		]

		shortlistedFoods = []

		# add items into the array list using randomizer
		for x in range(0, 8):
			#if counter is less than 3 take 2 items from set 1
			if (len(shortlistedFoods) < 2):
				randomInt = random.randint(0, (len(foodSet1) - 1))
				
				foodItem = Food(foodSet1[randomInt], set1Desc[randomInt], set1Img[randomInt])
				del foodSet1[randomInt]
				del set1Desc[randomInt]
				del set1Img[randomInt]

			#if counter is less than 7, take another 3 items from set 2
			elif (len(shortlistedFoods) < 5):
				randomInt = random.randint(0, (len(foodSet2) - 1))

				foodItem = Food(foodSet2[randomInt], set2Desc[randomInt], set2Img[randomInt])
				del foodSet2[randomInt]
				del set2Desc[randomInt]
				del set2Img[randomInt]

			#for the remaining loops, take items from set 3	
			else:
				randomInt = random.randint(0, (len(foodSet3) - 1))

				foodItem = Food(foodSet3[randomInt], set3Desc[randomInt], set3Img[randomInt])
				del foodSet3[randomInt]
				del set3Desc[randomInt]
				del set3Img[randomInt]

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
						 # "imageUri": "https://sethlui.com/wp-content/uploads/2015/06/penang-street-hawker-food.jpg",
						 "imageUri": foods.getFoodUrl(),
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


		# this section is for LINE platform
		lineData = {
			"payload": {
				"line":{
					"type": "template",
					"altText": "Best foods in Penang.",
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

		for x in range(len(shortlistedFoods)):
			foods = shortlistedFoods[x]

			lineCarousel.append(
				{
					"thumbnailImageUrl": foods.getFoodUrl(),
					"imageBackgroundColor": "#FFFFFF",
					"title": (foods.getFoodName())[:40],
					"text": (foods.getFoodDesc())[:60],
					"actions": [
						{
							"type": "uri",
							"label": "Find where",
							"uri": "https://www.google.com/maps/search/?api=1&query=" + (foods.getFoodName()).replace(' ', '+')
						}
					]
				}
			)				

		data["fulfillmentMessages"].append(lineData)

		data["fulfillmentMessages"].append(
			{
				"quickReplies": {
					"title": "Explore other options!",
					"quickReplies": [
						"🍲 Best foods", "🌈 Highlights", "💡Did you know/Tips", "Menu"
					]
				}	
			}
		)

		return data

	elif postedReq.get('action') == "jk-PenangInfo.jk-PenangInfo-highlights":
		highlightSet1 = [
			"Gravity Z", "ESCAPE Waterpark",
			"Avatar Secret Garden", "Penang Little India",
			"Penang Peranakan Mansion", "St. George's Church",
			"Kek Lok Si Temple", "Penang Hill",
			"Penang Street Art", "Snake Temple",
			"Penang National Park", "Tropical Spice Garden"
		]

		highlightSet2 = [
			"Fort Cornwallis", "Khoo Kongsi", 
			"Hin Bus Depot", "Entopia",
			"Clan Jetties of Penang", "The TOP, KOMTAR",
			"Batu Ferringhi Beach", "Tech Dome",
			"Penang Botanical Gardens", "Dharmikarama Burmese Temple",
			"Floating Mosque", "Arulmigu Balathandayuthapani Temple",
		]

		shortlistHighlights = []

		for x in range(0, 6):
			if (len(shortlistHighlights) < 5):
				randomInt = random.randint(0, (len(highlightSet1) - 1))

				placeItem = highlightSet1[randomInt]
				del highlightSet1[randomInt]

			else:
				randomInt = random.randint(0, (len(highlightSet2) - 1))

				placeItem = highlightSet2[randomInt]
				del highlightSet2[randomInt]

			shortlistHighlights.append(placeItem)

		# format data to be returned
		data = {
			"fulfillmentMessages":[
				{
					"text":{
						"text":[
							"These are the best places to visit in Penang!"
						]
					}
				}
			]
		}

		for x in range(len(shortlistHighlights)):
			highlight = shortlistHighlights[x]

			requestLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyARXZAr7XVLsPTI1e6veB99zuUmjYQEagI&rankby=distance&location=5.4356,100.3091"
			requestLink += "&keyword=" + highlight.replace(' ', '+')

			highlightResult = json.loads(urllib.request.urlopen(requestLink).read())
			results = highlightResult.get("results")
			stringTypes = ""
			photoURL = ""

			#if there are results
			if (highlightResult.get("status") == "OK"):
				for items in results:
					#get types that categorise the place
					if ("types" in items):
						types = items["types"]

						counter = 0
						for x in types:
							stringTypes += x + ", "
							counter += 1

							if counter == 2:
								break

						#remove last 2 characters of the string
						stringTypes = stringTypes[:-2]
						
						if '_' in stringTypes:
							stringTypes = stringTypes.replace('_', " ")

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

			
			if photoURL == "":
				photoURL = "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png"

			if stringTypes == "":
				stringTypes = "Highlight in Penang"

			showMap = "https://www.google.com/maps/search/?api=1&query=" + highlight

			data["fulfillmentMessages"].append(
				{
					"card": { 
						 "title": highlight,
						 "subtitle": stringTypes,
						 "imageUri": photoURL,
						 "buttons": [
						 	{
						 		"text": "Map",
						 		#link to open in google maps
						 		"postback": showMap.replace(' ', '+')
						 	}
						 ]
					}
				}
			)

		# # this section is for LINE platform
		# lineData = {
		# 	"payload": {
		# 		"line":{
		# 			"type": "template",
		# 			"altText": "Highlights to visit in Penang.",
		# 			"template": {
		# 				"type": "carousel",
		# 				"columns": [
							
		# 				],
						
		# 				"imageAspectRatio": "rectangle",
		# 				"imageSize": "cover"
		# 			}
		# 		}
		# 	}				
		# }

		# lineCarousel = lineData["payload"]["line"]["template"]["columns"]

		# for x in range(len(shortlistHighlights)):
		# 	highlightItem = shortlistHighlights[x]

		# 	lineCarousel.append(
		# 		{
		# 			"thumbnailImageUrl": photoURL,
		# 			"imageBackgroundColor": "#FFFFFF",
		# 			"title": highlightItem[:40],
		# 			"text": stringTypes[:60],
		# 			"actions": [
		# 				{
		# 					"type": "uri",
		# 					"label": "Map",
		# 					"uri": showMap.replace(' ', '+')
		# 				}
		# 			]
		# 		}
		# 	)				

		# data["fulfillmentMessages"].append(lineData)

		data["fulfillmentMessages"].append(
			{
				"quickReplies": {
					"title": "Explore other options!",
					"quickReplies": [
						"🍲 Best foods", "🌈 Highlights", "💡Did you know/Tips", "Menu"
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

