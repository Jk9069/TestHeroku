import urllib
import json
import os

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

def getWebhookResult(postReq):
	if postReq.get("queryResult").get("action") == "weather":
		
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

		speech = mainWeather + " with temperatures ranging from " + str(tempMinRange) 
		+ " to " + str(tempMaxRange) + " Celsius in " + weatherResult.get('name')

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

