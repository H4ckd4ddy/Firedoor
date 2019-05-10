from urllib.parse import unquote

class rules_manager():
	
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if len(get) > 0:
			if get[0] == 'rules':
				with open(database.get('config_directory')+'static_rules.conf', 'r') as rules_file:
					return 200, rules_file.read()
		if 'rules' in post:
			with open(database.get('config_directory')+'static_rules.conf', 'w') as rules_file:
				rules_file.write(unquote(unquote(post['rules'])).replace('+', ' '))
				return 200,'OK'
		return rules_manager.return_interface(database)
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			with open(database.get('config_directory')+'static_rules.conf') as rules_file:  
				html = interface.read()
				return 200, html