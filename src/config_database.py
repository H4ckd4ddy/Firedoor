import os
import json

class database:
	
	file = None
	database = None
	
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
	def get(cls, key, module='general_settings'):
		try:
			value = cls.database[module][key]
		except:
			value = None
		return value
	
	@classmethod
	def set(cls, key, value, module='general_settings'):
		if module not in cls.database:
			cls.database[module] = {}
		cls.database[module][key] = value
		cls.export_to_file()
	
	@classmethod
	def rem(cls, key, module='general_settings'):
		del cls.database[module][key]
		if len(cls.database[module]) == 0:
			del cls.database[module]
		cls.export_to_file()