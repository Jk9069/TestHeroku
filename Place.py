import random

class Place():
	def __init__(self, placeID, placeName, rating, openNow):
		self.placeID = placeID
		self.placeName = placeName
		self.rating = rating
		self.openNow = openNow

	def getPlaceName(self):
		return self.placeName

	def getRating(self):
		numRating = float(self.rating)

		if (numRating == 5 or numRating >= 4.5):
			starEmoji = "⭐⭐⭐⭐⭐"
		elif (numRating == 4 or numRating >= 3.5):
			starEmoji = "⭐⭐⭐⭐"
		elif (numRating == 3 or numRating >= 2.5):
			starEmoji = "⭐⭐⭐"
		elif (numRating == 2 or numRating >= 1.5):
			starEmoji = "⭐⭐"
		elif (numRating == 1 or numRating >= 0.5):
			starEmoji = "⭐"
		elif (numRating == 0):
			starEmoji = "No ratings yet."

		return starEmoji

	def getOpenNow(self):
		openStatus = ""
		
		if (self.openNow == 'true'):
			openStatus = "Open Now."
		else:
			openStatus = "Closed."

		return openStatus
		