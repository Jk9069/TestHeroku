import random

class Food():
	def __init__ (self, foodName, foodDesc):
		self.foodName = foodName
		self.foodDesc = foodDesc

	def getFoodName(self):
		return self.foodName

	def getFoodDesc(self):
		return self.foodDesc
