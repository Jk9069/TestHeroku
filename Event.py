
class Event():
	def __init__(self, eventName, eventVenue, dateTime, eventUrl, imgUrl):
		self.eventName = eventName
		self.eventVenue = eventVenue
		self.dateTime = dateTime
		# self.eventDesc = eventDesc
		self.eventUrl = eventUrl
		self.imgUrl = imgUrl

	def getEventName(self):
		return self.eventName

	def getEventVenue(self):
		return self.eventVenue

	def getEventDateTime(self):
		return self.dateTime

	# def getEventDesc(self):
	# 	return self.eventDesc

	def getEventUrl(self):
		return self.eventUrl

	def getImgUrl(self):
		return self.imgUrl
