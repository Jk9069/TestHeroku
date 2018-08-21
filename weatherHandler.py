

#define what temperature is considered hot / cool / warm
def getHotCold(temp):
	hotCold = ""

	if (temp >= 30):
		hotCold = "hot"
	elif (temp <= 23):
		hotCold = "cool"
	elif (temp > 23 and temp < 30):
		hotCold = "warm"

	return hotCold

#perform housekeeping to value of the parameter
def getOutputContextTimePeriod(postReq):
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
