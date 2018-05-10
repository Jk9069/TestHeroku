import urllib
import json
import os
import random

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

def getHotCold(temp):
	hotCold = ""

	if (temp >= 30):
		hotCold = "hot"
	elif (temp <= 23):
		hotCold = "cool"
	elif (temp > 23 and temp < 30):
		hotCold = "warm"

	return hotCold

def getOutputContextTimePeriod(postReq):
	outputContexts = postReq.get("outputContexts")
	for item in outputContexts:
		parameters = item["parameters"]

	#ex: morning, afternoon, night
	timePeriod = parameters.get("time-period.original")
	#ex: tomorrow, in 3 days
	date = parameters.get("date.original")

	if ('?' in timePeriod):
		timePeriod = timePeriod.replace('?','')
	if ('?' in date):
		date = date.replace('?', '')

	if (timePeriod == ""):
		speech = (" " + date)
	elif (timePeriod != "" and date != ""):
		speech = (" " + date + " " + timePeriod)
	elif (date == ""):
		if (timePeriod != "tonight"):
			speech = (" in the " + timePeriod)
		else:
			speech = (" " + timePeriod)

	return speech

def getWebhookResult(postReq):
	postedReq = postReq.get("queryResult")
	postedReqParams = postReq.get("queryResult").get("parameters")

	if postedReq.get("action") == "weather":
		#user just says 'weather'
		if ((postedReqParams.get("date") == "" and postedReqParams.get("time-period") == "" and postedReqParams.get("customLocation") == "") or (postedReqParams.get("customLocation") == "Penang" or postedReqParams.get("customLocation") == "Pulau Pinang")):
			#making request to OpenWeather API		
			#speech = "The weather is clear";
			weatherUrl = "https://api.openweathermap.org/data/2.5/weather?q=Penang&APPID=5b39dc8cce894f4233c14ed2ad3d7c44&units=metric"
			weatherResult = json.loads(urllib.request.urlopen(weatherUrl).read())
			print(weatherResult)

			#weatherData is a JSON list
			weatherData = weatherResult.get('weather')
			for item in weatherData:
				mainWeather = item['main']

			tempMinRange = weatherResult.get('main').get('temp_min')
			tempMaxRange = weatherResult.get('main').get('temp_max')

			hotCold = getHotCold(tempMaxRange)

			speech = (
				"It is going to be " + hotCold + " today. Weather is " + mainWeather + 
				" with temperatures ranging from " 
				+ str(tempMinRange) + " to " + str(tempMaxRange) 
				+ " Celsius in " + weatherResult.get('name')
			)

		#handles forecasts
		elif (postedReqParams.get("time-period") != ""):
			startTime = postedReqParams.get("time-period").get("startTime")
			queryDate = startTime[0:-15]
			print(queryDate)
			#slice the string to get hour, slice 11 characters from front and 12 from the back
			startTime = startTime[11:-12]
			print(startTime)
			endTime = postedReqParams.get("time-period").get("endTime")
			endTime = endTime[11:-12]
			print(endTime)

			weatherUrl = "https://api.openweathermap.org/data/2.5/forecast?q=Penang&APPID=5b39dc8cce894f4233c14ed2ad3d7c44&units=metric"
			weatherResult = json.loads(urllib.request.urlopen(weatherUrl).read())
			print(weatherResult)

			#weatherData is a JSON list
			weatherData = weatherResult.get('list')
			shortlistedData = []
			shortlistedTemp = []
			found = False
			for item in weatherData:
				#get date of the forecast
				forecastTime = item['dt_txt']
				forecastDate = forecastTime[0:-9]
				print(forecastDate)
				forecastTime = forecastTime[11:-6]
				print(forecastTime)

				if (queryDate == forecastDate):
					found = True
					if (forecastTime >= startTime and forecastTime <= endTime):
						shortlistedData.append(item['weather'])
						shortlistedTemp.append(item['main'].get('temp'))
				elif (found == True):
					break

			#randomly select shortlisted data and get the weather
			#provided range is between -1 and the size of the shortlisted data
			randomInt = random.randint(0, (len(shortlistedData)-1))
			mainWeather = shortlistedData[randomInt]
			for item in mainWeather:
				mainWeather = item['main']
				mainTemp = shortlistedTemp[randomInt]

			hotCold = getHotCold(mainTemp)
			forecastDetail = getOutputContextTimePeriod(postedReq)

			speech = (
				"It is going to be " + hotCold + forecastDetail
				+ ". Expected weather is " + mainWeather + " at " + str(mainTemp) + " Celsius."
			)

		elif (postedReqParams.get("date") != ""):
			queryDate = postedReqParams.get("date")
			queryDate = queryDate[0:-15]

			weatherUrl = "https://api.openweathermap.org/data/2.5/forecast?q=Penang&APPID=5b39dc8cce894f4233c14ed2ad3d7c44&units=metric"
			weatherResult = json.loads(urllib.request.urlopen(weatherUrl).read())
			print(weatherResult)

			#weatherData is a JSON list
			weatherData = weatherResult.get('list')
			found = False
			for item in weatherData:
				#get date of the forecast
				forecastTime = item['dt_txt']
				forecastDate = forecastTime[0:-9]
				#print(forecastDate)

				if (queryDate == forecastDate):
					found = True
					for data_items in item['weather']:
						mainWeather = data_items['main']

					mainTemp = item['main'].get('temp')
					break
				elif (found == True):
					break

			hotCold = getHotCold(mainTemp)
			forecastDetail = getOutputContextTimePeriod(postedReq)

			speech = (
				"It is going to be " + hotCold + forecastDetail
				+ ". Expected weather is " + mainWeather + " at " + str(mainTemp) + " Celsius."
			)

		return {
			#"speech": speech,
			#"displayText": speech,
			"fulfillmentText": speech,
			"source": 'OpenWeatherAPI'	
		}


#main
if __name__ == "__main__":
	port = int(os.getenv('PORT', 5000))
	#print ("Starting app on port %d" %(port))
	app.run(debug=True, port=port, host='0.0.0.0')

