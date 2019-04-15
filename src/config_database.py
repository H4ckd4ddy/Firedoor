import os
import json

class database:
	
	file = None
	database = None
	runtime_space = {}
	
	@classmethod
	def init(cls, file):
		if os.path.isfile(file):
			cls.file = file
			cls.import_from_file()
	
	@classmethod
	def import_from_file(cls):
		with open(cls.file) as json_file:
			cls.database = json.load(json_file)
	
	@classmethod
	def export_to_file(cls):
		with open(cls.file, 'w') as json_file:
			json.dump(cls.database, json_file, indent=4)
	
	@classmethod
	def get(cls, key):
		return cls.database[key]
	
	@classmethod
	def set(cls, key, value):
		cls.database[key] = value
		cls.export_to_file()
	
	@classmethod
	def rem(cls, key):
		del cls.database[key]
		cls.export_to_file()