import sys
import os

class analyzer:

	obj = None
	path = None

	def __init__(self, directory, analyzer_name):
		if os.path.isdir(directory+'/'+analyzer_name):
			self.path = directory+'/'+analyzer_name
			sys.path.insert(0, self.path)
			analyzer = __import__(analyzer_name)
			self.obj = getattr(analyzer, analyzer_name)

class analyzers_manager:

	analyzers = {}

	@classmethod
	def import_analyzers(cls):
		directory = 'analyzers'
		if os.path.isdir(directory):
			for analyzer_name in sorted(os.listdir(directory)):
				if analyzer_name not in cls.analyzers:
					cls.analyzers[analyzer_name] = analyzer(directory, analyzer_name)