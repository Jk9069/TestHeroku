import urllib
import json
import os
import random
import re

from Event import Event
from emoji import UNICODE_EMOJI

from flask import Flask
from flask import request
from flask import make_response

class eventFinder():

	def __init__(self, parameters):
		self.userQuery = parameters.get("eventConcert") 
		self.datePeriod = parameters.get("date-period")
		self.date = parameters.get("date")

	def performSearch(self):
		# need to search by category? mostly not more than 9 results de wor
		# categories = [
		# 	"learning_education", "music", "science", 
		# 	"business", "support", "outdoors_recreation", 
		# 	"performing_arts", "religion_spirituality",
		# 	"miscellaneous"
		# ]

		requestLink = "http://api.eventful.com/json/events/search?app_key=ccLj6sppM4RsQ4wX&location=George%20town,Pulau%20Pinang"

		# get the time period or date to search	
		if (self.datePeriod != ""):
			startDate = self.datePeriod.get("startDate")
			# print('STARTDATE: ' + startDate)

			startDate = (startDate[:10]).replace('-', '') + '00'
			# print('REPLACED STARTDATE: ' + startDate)

			endDate = self.datePeriod.get("endDate")
			# print('ENDDATE: ' + endDate)

			endDate = (endDate[:10]).replace('-', '') + '00'
			# print('REPLACED ENDDATE: ' + endDate)

			requestLink = requestLink + "&date=" + str(startDate) + "-" + str(endDate)
		
		elif self.date != "":
			# date = postedReqParams.get("date")
			# print ('DATE: ' + date)

			date = (self.date[:10]).replace('-', '') + "00"
			# print('REPLACED DATE: ' + date)

			requestLink = requestLink + "&date=" + str(date) + "-" + str(date)


		#start search here
		#requestLink = requestLink + "&category=" + "???"
		print (requestLink)
		eventResult = json.loads(urllib.request.urlopen(requestLink).read())
		allEvents = []
		counter = 0

		# pluck information from results
		# need to handle if more than 9 results????
		if (eventResult.get("total_items") != "0"):
			events = eventResult.get("events").get("event")

			for item in events:
				eventfulUrl = item.get("url")

				timeDate = item.get("start_time")
				#description = item.get("description")
				eventName = item.get("title")

				if item.get("image") != None:
					if item.get("image").get("small") != None:
						imageUrl = item.get("image").get("small").get("url")
						imageUrl = imageUrl.replace('small', 'large')
					else:
						imageUrl = item.get("image").get("medium").get("url")
						imageUrl = imageUrl.replace('small', 'large')
				else:
					imageUrl = "https://s3.amazonaws.com/mashape-production-logos/apis/53aa61b1e4b0a798dbd1c000_medium"
				
				venue = item.get("venue_name")

				newEvent = Event(eventName, venue, timeDate, eventfulUrl, imageUrl)

				allEvents.append(newEvent)
				counter += 1

				if (counter > 7):
					break

			data = {
				"source": "Eventful API", 	
				"fulfillmentMessages":[
					{
						"text":{
							"text":[
								"Here's what I found."
							]
						}
					} 
				]
			}

			for x in range(len(allEvents)):
				event = allEvents[x]

				# if (x != 8):
				data["fulfillmentMessages"].append(
					{
						"card": { 
							 "title": event.getEventName(),
							 "subtitle": event.getEventVenue() + "\n" + event.getEventDateTime() + "\n" + "Powered by Eventful",
							 # "imageUri": event.getImgUrl(),
							 "imageUri": "https://s3.amazonaws.com/mashape-production-logos/apis/53aa61b1e4b0a798dbd1c000_medium",
							 "buttons": [
							 	{
							 		"text": "View on Eventful",
							 		#link to open in google maps
							 		"postback": event.getEventUrl()
							 	}
							 ]
						}
					}
				)

				if counter == 7:
					break

			# this section is for LINE platform
			lineData = {
				"payload": {
					"line":{
						"type": "template",
						"altText": "Results found.",
						"template": {
							"type": "carousel",
							"columns": [
								# {
								# 	"thumbnailImageUrl": "https://s3.amazonaws.com/mashape-production-logos/apis/53aa61b1e4b0a798dbd1c000_medium",
								# 	"imageBackgroundColor": "#FFFFFF",
								# 	"title": "This is the title",
								# 	"text": "This is the description", #+ "\n" + event.getEventDateTime(),
								# 	"actions": [
								# 		{
								# 			"type": "uri",
								# 			"label": "Map",
								# 			"uri": "https://www.google.com/?client=safari&channel=iphone_bm"
								# 		}
								# 	]
								# }
							],
							
							"imageAspectRatio": "rectangle",
							"imageSize": "cover"
						}
					}
				}				
			}

			lineCarousel = lineData["payload"]["line"]["template"]["columns"]

			for y in range(len(allEvents)):
				event = allEvents[y]

				if y < 7:
					lineCarousel.append(
						{
							# image must be https but API do not have https links
							"thumbnailImageUrl": "https://s3.amazonaws.com/mashape-production-logos/apis/53aa61b1e4b0a798dbd1c000_medium",
							"imageBackgroundColor": "#FFFFFF",
							"title": (event.getEventName())[:40],
							"text": (event.getEventVenue() + "\n" + event.getEventDateTime())[:60],
							"actions": [
								{
									"type": "uri",
									"label": "Map",
									"uri": event.getEventUrl()
								}
							]
						}
					)				

			data["fulfillmentMessages"].append(lineData)

			data["fulfillmentMessages"].append(
				{	
					"text": {
						"text": [
							"💡 Tip: You can search for future events as well. \n\nEg. 'Events next week', 'Events next month'"
						]
					}					
				}
			)

			data["fulfillmentMessages"].append(
				{	
					"quickReplies": {
						"title": "What else can I help you with?",
						"quickReplies": [
							"Weather", "Travel Purpose", "About Penang", "Bye!"
						]
					}					
				}
			)

			return data	

		else:
			data = {
				"fulfillmentText": "No results found :("
			}

			return data
