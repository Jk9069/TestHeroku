import urllib
import json
import os
import random

from flask import Flask
from flask import request
from flask import make_response

class weatherResponse():
#	def __init__(self, postedReqParams, postedReq):
#		self.postedReqParams = postedReqParams
#		self.postedReq = postedReq

	def setter(self, postedReqParams, postedReq):
		self.postedReqParams = postedReqParams
		self.postedReq = postedReq

	#define what temperature is considered hot / cool / warm
	def getHotCold(self, temp):
		hotCold = ""

		if (temp >= 30):
			hotCold = "hot"
		elif (temp <= 23):
			hotCold = "cool"
		elif (temp > 23 and temp < 30):
			hotCold = "warm"

		return hotCold

	#perform housekeeping to value of the parameter
	def getOutputContextTimePeriod(self, postReq):
		outputContexts = postReq.get("outputContexts")
		for item in outputContexts:
			parameters = item["parameters"]

		#ex: morning, afternoon, night
		timePeriod = parameters.get("time-period.original")
		#ex: tomorrow, in 3 days
		date = parameters.get("date.original")

		#remove the ? that is not ignored by the bot
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

	def mainWeatherMessage(self, mainWeather):
		if ('Clear' in mainWeather):
			text = "Any plans for such weather?"
		elif ('Clouds' in mainWeather):
			text = "Let's hope it doesn't rain anytime soon!"
		elif ('Rain' in mainWeather or 'drizzle' in mainWeather):
			text = "Aww, I miss the sun already."
		elif ('Thunderstorm' in mainWeather):
			text = "Yikes! Remember to stay dry indoors."
		else:
			text = "Weather in Penang is so predictable.. as long as it doesn't snow."

		return text

	def getWeatherResponse(self):
		#user just says 'weather'
			if ((self.postedReqParams.get("date") == "" and self.postedReqParams.get("time-period") == "" and self.postedReqParams.get("customLocation") == "") or (self.postedReqParams.get("customLocation") == "Penang" or self.postedReqParams.get("customLocation") == "Pulau Pinang")):
				#making request to OpenWeather API		
				#speech = "The weather is clear";
				weatherUrl = "https://api.openweathermap.org/data/2.5/weather?q=Penang&APPID=5b39dc8cce894f4233c14ed2ad3d7c44&units=metric"
				weatherResult = json.loads(urllib.request.urlopen(weatherUrl).read())
				print(weatherResult)

				#weatherData is a JSON list
				weatherData = weatherResult.get('weather')
				for item in weatherData:
					mainWeather = item['main']
					icon = item['icon']

				tempMinRange = weatherResult.get('main').get('temp_min')
				tempMaxRange = weatherResult.get('main').get('temp_max')

				hotCold = self.getHotCold(tempMaxRange)

				speech = (
					"It is going to be " + hotCold + " today. Weather is " + mainWeather + 
					" with temperatures ranging from " 
					+ str(tempMinRange) + " to " + str(tempMaxRange) 
					+ " Celsius in " + weatherResult.get('name')
				)

			#handles forecasts
			elif (self.postedReqParams.get("time-period") != ""):
				startTime = self.postedReqParams.get("time-period").get("startTime")
				queryDate = startTime[0:-15]
				print(queryDate)
				#slice the string to get hour, slice 11 characters from front and 12 from the back
				startTime = startTime[11:-12]
				print(startTime)
				endTime = self.postedReqParams.get("time-period").get("endTime")
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
					icon = item['icon']
					mainTemp = shortlistedTemp[randomInt]

				hotCold = self.getHotCold(mainTemp)
				forecastDetail = self.getOutputContextTimePeriod(self.postedReq)

				speech = (
					"It is going to be " + hotCold + forecastDetail
					+ ". Expected weather is " + mainWeather + " at " + str(mainTemp) + " Celsius."
				)

			elif (self.postedReqParams.get("date") != ""):
				queryDate = self.postedReqParams.get("date")
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
							icon = data_items['icon']

						mainTemp = item['main'].get('temp')
						break
					elif (found == True):
						break

				hotCold = self.getHotCold(mainTemp)
				forecastDetail = self.getOutputContextTimePeriod(self.postedReq)

				speech = (
					"It is going to be " + hotCold + forecastDetail
					+ ". Expected weather is " + mainWeather + " at " + str(mainTemp) + " Celsius."
				)

			return {
				#"speech": speech,
				#"displayText": speech,
				#"fulfillmentText": speech,
				"fulfillmentText": "This is optional",
				"fulfillmentMessages": [
					{
						"card": {
							"title": "Weather forecast",
							"subtitle": speech,
							"imageUri": "http://openweathermap.org/img/w/" + icon + ".png"
							#"buttons": [
							#	{
							#		"text": "button text",
							#		"postback": ""
							#	}
							#]
						}
					},
					{
						"text": {
							"text": [
								self.mainWeatherMessage(mainWeather)
							]
						}
					},
					{
						#have to change to quick replies
						"text":{
							"text": [
								"Do you want me to suggest suitable places to visit?"
							]
						}
					}
				],
				"source": 'OpenWeatherAPI',
				"outputContexts": [
					{
					    "lifespanCount": 5,
					    "parameters": {
					    	"mainWeather": mainWeather
					    }
					}
				]	
			}



