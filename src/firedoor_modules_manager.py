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
	def import_modules(cls):
		cls.import_modules_from_dir('core_modules')
		cls.import_modules_from_dir('modules')

	@classmethod
	def import_modules_from_dir(cls, directory):
		directory = directory.rstrip('/')
		if os.path.isdir(directory):
			for module_name in sorted(os.listdir(directory)):
				if module_name not in cls.modules:
					cls.modules[module_name] = module(directory, module_name)

	@classmethod
	def install_modules(cls, public):
		for module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'install_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.install_entrypoint(public)
				os.chdir(public['base_directory'])

	@classmethod
	def uninstall_modules(cls, public):
		for module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'uninstall_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.uninstall_entrypoint(public)
				os.chdir(public['base_directory'])

	@classmethod
	def run_cli_module(cls, public, module_name, args):
		if module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'cli_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.cli_entrypoint(public, args)
				os.chdir(public['base_directory'])
			else:
				print('Module "{}" does not have cli interface'.format(module_name))
		else:
			print('Module "{}" does no exist'.format(module_name))

	@classmethod
	def startup_modules(cls, public):
		for module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'startup_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.startup_entrypoint(public)
				os.chdir(public['base_directory'])