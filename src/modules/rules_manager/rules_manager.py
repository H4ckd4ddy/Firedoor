from urllib.parse import unquote
import json

class rules_manager():
	
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if 'rules' in post:
			with open(database.get('config_directory')+'static_rules.conf', 'w') as rules_file:
				new_rules = unquote(unquote(post['rules'])).replace('+', ' ')
				new_rules = json.dumps(json.loads(new_rules), indent=4)
				rules_file.write(new_rules)
				return 200,'OK'
		elif len(get) > 0:
			if get[0] == 'rules':
				with open(database.get('config_directory')+'static_rules.conf', 'r') as rules_file:
					return 200, rules_file.read()
		return rules_manager.return_interface(database)
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			with open(database.get('config_directory')+'static_rules.conf') as rules_file:  
				html = interface.read()
				return 200, html