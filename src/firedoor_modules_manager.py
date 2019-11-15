import sys
import os
from config_database import database

class module:

	name = None
	obj = None
	path = None
	required = False
	enable = False

	def __init__(self, directory, module_name, required=False):
		if os.path.isdir(directory+'/'+module_name):
			self.name = module_name
			self.required = required
			self.path = database.get('base_directory')+'/'+directory+'/'+module_name
			sys.path.insert(0, self.path)
			module = __import__(module_name)
			self.obj = getattr(module, module_name)
			self.enable = self.is_enable()

	def is_enable(self):
		if (self.name in database.get('activated_modules') and database.get('activated_modules')[self.name]) or self.required:
			return True
		else:
			return False

	def change_state(self, desirate_state):
		if not self.required:
			activated_modules = database.get('activated_modules')
			if desirate_state:
				activated_modules[self.name] = True
				self.enable = True
			else:
				activated_modules[self.name] = False
				self.enable = False
			database.set('activated_modules', activated_modules)

class modules_manager:

	modules = {}

	@classmethod
	def import_modules(cls):
		cls.import_modules_from_dir('core_modules', True)
		cls.import_modules_from_dir('modules')

	@classmethod
	def import_modules_from_dir(cls, directory, required_modules=False):
		directory = directory.rstrip('/')
		if os.path.isdir(directory):
			for module_name in sorted(os.listdir(directory)):
				if module_name not in cls.modules:
					cls.modules[module_name] = module(directory, module_name, required_modules)

	@classmethod
	def install_modules(cls):
		activated_modules = database.get('activated_modules')
		for module_name in cls.modules:
			if module_name not in activated_modules:
				if cls.modules[module_name].required:
					activated_modules[module_name] = True
				else:
					activated_modules[module_name] = False
			if hasattr(cls.modules[module_name].obj, 'install_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.install_entrypoint()
				os.chdir(database.get('base_directory'))
		database.set('activated_modules', activated_modules)

	@classmethod
	def uninstall_modules(cls):
		for module_name in cls.modules:
			if hasattr(cls.modules[module_name].obj, 'uninstall_entrypoint'):
				os.chdir(cls.modules[module_name].path)
				cls.modules[module_name].obj.uninstall_entrypoint()
				os.chdir(database.get('base_directory'))

	@classmethod
	def run_cli_module(cls, module_name, args):
		if module_name in cls.modules:
			if cls.modules[module_name].enable:
				if hasattr(cls.modules[module_name].obj, 'cli_entrypoint'):
					os.chdir(cls.modules[module_name].path)
					cls.modules[module_name].obj.cli_entrypoint(args)
					os.chdir(database.get('base_directory'))
				else:
					print('Module "{}" does not have cli interface'.format(module_name))
			else:
				print('Module "{}" disabled'.format(module_name))
		else:
			print('Module "{}" does no exist'.format(module_name))

	@classmethod
	def run_web_module(cls, request_handler, module_name, get, post):
		if module_name in cls.modules:
			if cls.modules[module_name].enable:
				if hasattr(cls.modules[module_name].obj, 'web_entrypoint'):
					os.chdir(cls.modules[module_name].path)
					client_ip = request_handler.client_address[0]
					status, content = cls.modules[module_name].obj.web_entrypoint(client_ip, get, post)
					os.chdir(database.get('base_directory'))
					return status, content
				else:
					msg = 'Module "{}" does not have web interface'.format(module_name)
					return 404, msg
			else:
				msg = 'Module "{}" disabled'.format(module_name)
				return 404, msg
		else:
			msg = 'Module "{}" does no exist'.format(module_name)
			return 404, msg

	@classmethod
	def startup_modules(cls):
		for module_name in cls.modules:
			if cls.modules[module_name].enable:
				if hasattr(cls.modules[module_name].obj, 'startup_entrypoint'):
					os.chdir(cls.modules[module_name].path)
					cls.modules[module_name].obj.startup_entrypoint()
					os.chdir(database.get('base_directory'))

	@classmethod
	def broadcast_event(cls, event):
		for module_name in cls.modules:
			if cls.modules[module_name].enable:
				if hasattr(cls.modules[module_name].obj, 'event_listener'):
					os.chdir(cls.modules[module_name].path)
					cls.modules[module_name].obj.event_listener(event)
					os.chdir(database.get('base_directory'))

	@classmethod
	def get_optional_modules_list(cls):
		modules = {}
		for module_name in cls.modules:
			if module_name not in modules and not cls.modules[module_name].required:
				if cls.modules[module_name].is_enable():
					modules[module_name] = True
				else:
					modules[module_name] = False
		return modules