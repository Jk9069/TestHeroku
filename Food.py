import random

class Food():
	def __init__ (self, foodName, foodDesc, foodUrl):
		self.foodName = foodName
		self.foodDesc = foodDesc
		self.foodUrl = foodUrl

	def getFoodName(self):
		return self.foodName

	def getFoodDesc(self):
		return self.foodDesc

	def getFoodUrl(self):
		return self.foodUrl
