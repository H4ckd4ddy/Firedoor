import os
import hashlib
import urllib.parse

class settings():
	
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if len(post) > 0:
			if 'action' in post:
				if post['action'] == 'change_settings':
					result = settings.change_settings(database, post)
					return settings.return_interface(database, result[0], result[1])
		if len(get) > 0:
			if get[0] == 'clear_ip':
				settings.clear_ip_blacklist(database)
				msg = 'IP blacklist cleared'
				return settings.return_interface(database, msg, 'green')
		return settings.return_interface(database)
	
	@staticmethod
	def change_settings(database, post):
		post_data = {}
		for key in post:
			if len(post[key]) > 0:
				post_data[key] = post[key]
		post_data = post
		if 'server' in post:
			database.set('server', post['server'])
		if 'password_1' in post:
			if len(post['password_1']) > 0:
				if post['password_1'] == post['password_2']:
					password_hash = hashlib.sha512(post['password_1'].encode('utf-8')).hexdigest()
					database.set('password', password_hash)
				else:
					return 'Passwords not match', 'red'
		if 'web_interface_port' in post:
			if post['web_interface_port'].isdigit():
				if int(post['web_interface_port']) != database.get('web_interface_port'):
					database.set('web_interface_port', int(post['web_interface_port']))
			else:
				return 'Port should contain only digits', 'red'
		if 'TLS' in post and post['TLS'] == 'on':
			database.set('TLS', True)
		else:
			database.set('TLS', False)
		if 'cert_path' in post:
			post['cert_path'] = urllib.parse.unquote(post['cert_path'])
			if post['cert_path'] != database.get('cert_path'):
				if os.path.exists(post['cert_path']) or database.get('TLS') == False:
					database.set('cert_path', post['cert_path'])
				else:
					return 'Certificate file not found', 'red'
		if 'key_path' in post:
			post['key_path'] = urllib.parse.unquote(post['key_path'])
			if post['key_path'] != database.get('key_path'):
				if os.path.exists(post['key_path']) or database.get('TLS') == False:
					database.set('key_path', post['key_path'])
				else:
					return 'Key file not found', 'red'
		return 'Settings saved','green'
	
	@staticmethod
	def clear_ip_blacklist(database):
		database.set('IP', [])
	
	@staticmethod
	def return_interface(database, msg='', color='white'):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{msg_color}}', color)
			html = html.replace('{{msg}}', msg)
			html = html.replace('{{web_interface_port}}', str(database.get('web_interface_port')))
			html = html.replace('{{TLS}}', 'checked' if database.get('TLS') else '')
			html = html.replace('{{cert_path}}', database.get('cert_path'))
			html = html.replace('{{key_path}}', database.get('key_path'))
			return 200, html