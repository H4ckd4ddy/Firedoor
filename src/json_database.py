import os
import json

class database:
	file = None
	database = None
	def __init__(self, file):
		if os.path.isfile(file):
			self.file = file
			self.import_from_file()
	
	def import_from_file(self):
		with open(self.file) as json_file:
			self.database = json.load(json_file)
	
	def export_to_file(self):
		with open(self.file, 'w') as json_file:
			json.dump(self.database, json_file, indent=4)
	
	def get(self, key):
		return self.database[key]
	
	def set(self, key, value):
		self.database[key] = value
		self.export_to_file()
	
	def rem(self, key):
		del self.database[key]
		self.export_to_file()