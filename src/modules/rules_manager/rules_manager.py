from urllib.parse import unquote

class rules_manager():
	
	@staticmethod
	def web_entrypoint(public, get, post):
		if 'rules' in post:
			with open(public['config_directory']+'static_rules.conf', 'w') as rules_file:
				rules_file.write(unquote(unquote(post['rules'])).replace('+', ' '))
		return rules_manager.return_interface(public)
	
	@staticmethod
	def return_interface(public):
		with open('interface.html', 'r') as interface:
			with open(public['config_directory']+'static_rules.conf') as rules_file:  
				html = interface.read()
				html = html.replace('{{static_rules}}', rules_file.read())
				return 200, html