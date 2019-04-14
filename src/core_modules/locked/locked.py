import os
import pyptables
from threading import Timer
from shutil import copyfile

class locked():
	
	@staticmethod
	def install_entrypoint(database):
		config_files_list = {
								'essential_rules.conf': 'essential_rules.conf',
								'default_static_rules.conf': 'static_rules.conf',
								'default_management_rules.conf': 'management_rules.conf'
							}
		for config_file in config_files_list:
			if not os.path.exists(database.get('config_directory')+config_files_list[config_file]):
				copyfile(config_file, database.get('config_directory')+config_files_list[config_file])

	@staticmethod
	def cli_entrypoint(database, args):
		if len(args) > 0:
			if args[0] == 'unlock':
				locked.unlock(database)
			else:
				locked.lock(database)
		else:
			print('Nothing to do')
	
	@staticmethod
	def startup_entrypoint(database):
		print('tmp')#locked.lock(database)
	
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if len(get) > 0:
			if get[0] == 'lock':
				locked.lock(database)
				return 200, '<script>document.location = "/"</script>'
		locked.unlock(database, client_ip)
		return locked.return_interface(database)
	
	@staticmethod
	def unlock(database, client_ip):
		print('Apply iptables rules')
		locked.flush_rules(database)
		locked.define_all_policies(database, 'DROP')
		locked.apply_rules_from(database, 'essential_rules.conf')
		locked.apply_rules_from(database, 'static_rules.conf')
		locked.apply_rules_from(database, 'management_rules.conf', client_ip)
		locked.start_timer(database)
	
	@staticmethod
	def apply_rules_from(database, file_name, client_ip=None):
		file_path = database.get('config_directory')+file_name
		if os.path.exists(file_path):
			iptables = pyptables.Iptables()
			iptables.import_from(file_path, client_ip)
	
	@staticmethod
	def flush_rules(database):
		iptables = pyptables.Iptables()
		iptables.flush()
	
	@staticmethod
	def define_all_policies(database, policy):
		iptables = pyptables.Iptables()
		iptables.change_policy(policy)
	
	@staticmethod
	def start_timer(database):
		t = Timer(60, locked.lock, [database])
		t.start()
	
	@staticmethod
	def lock(database):
		locked.flush_rules(database)
		locked.define_all_policies(database, 'DROP')
		locked.apply_rules_from(database, 'essential_rules.conf')
		locked.apply_rules_from(database, 'static_rules.conf')
		print('Closed '+database.get('server'))
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html