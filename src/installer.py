import os
import shutil
from shutil import copyfile
from firedoor_modules_manager import *

class installer:
	
	@classmethod
	def initialisation(cls, config_directory, import_disabled_modules=False):
		database.init(config_directory+'database.json')
		database.set('config_directory', config_directory)
		database.set('base_directory', cls.get_exe_path())
		os.chdir(database.get('base_directory'))
		modules_manager.import_modules(import_disabled_modules)
	
	@classmethod
	def install(cls, config_directory):
		if not os.path.isdir(config_directory):
			os.mkdir(config_directory)
		if not os.path.exists(config_directory+'database.json'):
			if hasattr(sys, '_MEIPASS'):
				base_directory = getattr(sys, '_MEIPASS', os.getcwd())
			else:
				base_directory = os.path.dirname(os.path.realpath(__file__))
			os.chdir(base_directory)
			copyfile('data_files/default_database.json', config_directory+'database.json')
		if not os.path.exists('/etc/systemd/system/firedoor.service') and os.path.isdir('/etc/systemd/system'):
			with open('data_files/firedoor.service', 'r') as default_service_file:
				service = default_service_file.read()
				service = service.replace('{{firedoor_path}}', sys.executable)
				with open('/etc/systemd/system/firedoor.service', 'w+') as service_file:
					service_file.write(service)
			os.system('systemctl enable firedoor.service')
		cls.initialisation(config_directory, True)
		modules_manager.install_modules()
		print('Firedoor successfully installed !')
	
	@classmethod
	def uninstall(cls, config_directory):
		cls.initialisation(config_directory, True)
		if cls.confirm_uninstall():
			modules_manager.uninstall_modules()
			if os.path.isdir(config_directory):
				shutil.rmtree(config_directory)
			print('Firedoor successfully removed !')
	
	@classmethod
	def confirm_uninstall(cls):
		choice = ''
		while choice not in ['y', 'n']:
			choice = input('Uninstall Firedoor and delete all configurations [y/n] ? ').lower()
		if choice == 'y':
			return True
		else:
			print('/!\\ Uninstallation aborted /!\\')
	
	@classmethod
	def get_exe_path(cls):
		if hasattr(sys, '_MEIPASS'):
			base_directory = getattr(sys, '_MEIPASS', os.getcwd())
		else:
			base_directory = os.path.dirname(os.path.realpath(__file__))
		return base_directory
	
	@classmethod
	def check_installation(cls, config_directory='/etc/firedoor/'):
		if os.path.exists(config_directory+'database.json'):
			return True
		else:
			return False