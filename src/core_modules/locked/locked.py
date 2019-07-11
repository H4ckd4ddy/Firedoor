import os
import pyptables
from threading import Timer
from shutil import copyfile
from config_database import database

class locked():
	
	@classmethod
	def install_entrypoint(cls):
		config_files_list = {
								'essential_rules.conf': 'essential_rules.conf',
								'default_static_rules.conf': 'static_rules.conf',
								'default_management_rules.conf': 'management_rules.conf',
								'default_block_rules.conf': 'block_rules.conf'
							}
		for config_file in config_files_list:
			if not os.path.exists(database.get('config_directory')+config_files_list[config_file]):
				copyfile(config_file, database.get('config_directory')+config_files_list[config_file])
	
	@classmethod
	def cli_entrypoint(cls, args):
		if len(args) > 0:
			if args[0] == 'unlock':
				cls.unlock()
			else:
				cls.lock()
		else:
			print('Nothing to do')
	
	@classmethod
	def startup_entrypoint(cls):
		try:
			cls.lock()
		except:
			pass
	
	@classmethod
	def event_listener(cls, event):
		if event['type'] == 'reload_rules':
			cls.lock()

	@classmethod
	def web_entrypoint(cls, client_ip, get, post):
		if len(get) > 0:
			if get[0] == 'lock':
				cls.lock()
				return 200, '<script>document.location = "/"</script>'
		cls.unlock(client_ip)
		return cls.return_interface()
	
	@classmethod
	def unlock(cls, client_ip):
		print('Apply iptables rules')
		cls.flush_rules()
		cls.define_all_policies('DROP')
		cls.apply_rules_from('block_rules.conf')
		cls.apply_rules_from('essential_rules.conf')
		cls.apply_rules_from('static_rules.conf')
		cls.apply_rules_from('management_rules.conf', client_ip)
		cls.start_timer()
	
	@classmethod
	def apply_rules_from(cls, file_name, client_ip=None):
		file_path = database.get('config_directory')+file_name
		if os.path.exists(file_path):
			iptables = pyptables.Iptables()
			iptables.import_from(file_path, client_ip)
	
	@classmethod
	def flush_rules(cls):
		iptables = pyptables.Iptables()
		iptables.flush()
	
	@classmethod
	def define_all_policies(cls, policy):
		iptables = pyptables.Iptables()
		iptables.change_policy(policy)
	
	@classmethod
	def start_timer(cls):
		t = Timer(60, cls.lock)
		t.start()
	
	@classmethod
	def lock(cls):
		cls.flush_rules()
		cls.define_all_policies('DROP')
		cls.apply_rules_from('block_rules.conf')
		cls.apply_rules_from('essential_rules.conf')
		cls.apply_rules_from('static_rules.conf')
	
	@classmethod
	def return_interface(cls):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html