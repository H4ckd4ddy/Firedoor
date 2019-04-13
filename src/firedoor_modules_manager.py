import sys
import os

class module:

	obj = None
	path = None

	def __init__(self, directory, module_name):
		if os.path.isdir(directory+'/'+module_name):
			self.path = directory+'/'+module_name
			sys.path.insert(0, self.path)
			module = __import__(module_name)
			self.obj = getattr(module, module_name)

class modules_manager:

	modules = {}

	@classmethod
	def import_modules_from_dir(cls, directory):
		directory = directory.rstrip('/')
		if os.path.isdir(directory):
			for module_name in sorted(os.listdir(directory)):
				if module_name not in cls.modules:
					cls.modules[module_name] = module(directory, module_name)

	@classmethod
	def import_modules(cls):
		cls.import_modules_from_dir('core_modules')
		cls.import_modules_from_dir('modules')

	@classmethod
	def startup_modules(cls, public):
		for module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'startup_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.startup_entrypoint(public)
				os.chdir(public['base_directory'])