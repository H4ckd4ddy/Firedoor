import os
import pyptables
from threading import Timer
from shutil import copyfile

class locked():
	
	@staticmethod
	def install_entrypoint(public):
		config_files_list = {
								'essential_rules.conf': 'essential_rules.conf',
								'default_static_rules.conf': 'static_rules.conf',
								'default_management_rules.conf': 'management_rules.conf'
							}
		for config_file in config_files_list:
			if not os.path.exists(public['config_directory']+config_files_list[config_file]):
				copyfile(config_file, public['config_directory']+config_files_list[config_file])

	@staticmethod
	def cli_entrypoint(public, args):
		if len(args) > 0:
			if args[0] == 'unlock':
				locked.unlock(public)
			else:
				locked.lock(public)
		else:
			print('Nothing to do')
	
	@staticmethod
	def startup_entrypoint(public):
		print('tmp')#locked.lock(public)
	
	@staticmethod
	def web_entrypoint(public, get, post):
		if len(get) > 0:
			if get[0] == 'lock':
				locked.lock(public)
				return 200, '<script>document.location = "/"</script>'
		locked.unlock(public)
		return locked.return_interface(public)
	
	@staticmethod
	def unlock(public):
		print('Apply iptables rules')
		locked.flush_rules(public)
		locked.define_all_policies(public, 'DROP')
		locked.apply_rules_from(public, 'essential_rules.conf')
		locked.apply_rules_from(public, 'static_rules.conf')
		locked.apply_rules_from(public, 'management_rules.conf')
		locked.start_timer(public)
	
	@staticmethod
	def apply_rules_from(public, file_name):
		file_path = public['config_directory']+file_name
		if os.path.exists(file_path):
			iptables = pyptables.Iptables()
			if 'client_ip' in public:
				client_ip = public['client_ip']
			else:
				client_ip = None
			iptables.import_from(file_path, client_ip)
	
	@staticmethod
	def flush_rules(public):
		iptables = pyptables.Iptables()
		iptables.flush()
	
	@staticmethod
	def define_all_policies(public, policy):
		iptables = pyptables.Iptables()
		iptables.change_policy(policy)
	
	@staticmethod
	def start_timer(public):
		t = Timer(60, locked.lock, [public])
		t.start()
	
	@staticmethod
	def lock(public):
		locked.flush_rules(public)
		locked.define_all_policies(public, 'DROP')
		locked.apply_rules_from(public, 'essential_rules.conf')
		locked.apply_rules_from(public, 'static_rules.conf')
		print('Closed '+public['database'].get('server'))
	
	@staticmethod
	def return_interface(public):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html