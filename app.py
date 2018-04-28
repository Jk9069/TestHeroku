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
	print(json.dumps(req, indent=4))

	#pass the post request to another function to obtain a result from API
	apiResult = getWebhookResult(postReq)

	#print out result (viewing purposes only)
	apiResult = json.dumps(apiResult, indent=4)
	print(result)

	#return result to chatbot to respond to user
	finResult = make_response(apiResult)
	finResult.headers['Content_Type'] = 'application/json'
	return finResult

def getWebhookResult(postReq):
	if postReq.get("queryResult").get("action") == "weather":
		
		speech = "The weather is clear";

		return {
			"speech": speech,
			"displayText": speech,

		}


#main
if __name__ == "__main__":
	port = int(os.getenv('PORT', 5000))
	#print ("Starting app on port %d" %(port))
	app.run(debug=True, port=port, host='0.0.0.0')

