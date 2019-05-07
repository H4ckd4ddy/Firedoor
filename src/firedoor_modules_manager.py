import sys
import os
from config_database import database

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
	def import_modules(cls, import_disabled_modules=False):
		cls.import_modules_from_dir('core_modules', True)
		cls.import_modules_from_dir('modules', import_disabled_modules)

	@classmethod
	def import_modules_from_dir(cls, directory, required_modules=False):
		directory = directory.rstrip('/')
		if os.path.isdir(directory):
			for module_name in sorted(os.listdir(directory)):
				if module_name not in cls.modules:
					if module_name in database.get('activated_modules') or required_modules:
						cls.modules[module_name] = module(directory, module_name)

	@classmethod
	def install_modules(cls):
		activated_modules = database.get('activated_modules')
		for module_name in cls.modules:
			if module_name not in activated_modules:
				activated_modules.append(module_name)
			if hasattr(cls.modules[module_name].obj, 'install_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.install_entrypoint(database)
				os.chdir(database.get('base_directory'))
		database.set('activated_modules', activated_modules)

	@classmethod
	def uninstall_modules(cls):
		for module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'uninstall_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.uninstall_entrypoint(database)
				os.chdir(database.get('base_directory'))

	@classmethod
	def run_cli_module(cls, module_name, args):
		if module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'cli_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.cli_entrypoint(database, args)
				os.chdir(database.get('base_directory'))
			else:
				print('Module "{}" does not have cli interface'.format(module_name))
		else:
			print('Module "{}" does no exist'.format(module_name))

	@classmethod
	def run_web_module(cls, request_handler, module_name, get, post):
		if module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'web_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				client_ip = request_handler.client_address[0]
				status, content = cls.modules[module_name].obj.web_entrypoint(database, client_ip, get, post)
				os.chdir(database.get('base_directory'))
				return status, content
			else:
				msg = 'Module "{}" does not have web interface'.format(module_name)
				return 404, msg
		else:
			msg = 'Module "{}" does no exist'.format(module_name)
			return 404, msg

	@classmethod
	def startup_modules(cls):
		for module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'startup_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.startup_entrypoint(database)
				os.chdir(database.get('base_directory'))