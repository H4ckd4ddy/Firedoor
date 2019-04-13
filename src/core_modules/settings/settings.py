import os
import hashlib
import urllib.parse

class settings():
	
	@staticmethod
	def web_entrypoint(public, get, post):
		if len(post) > 0:
			if 'action' in post:
				if post['action'] == 'change_settings':
					result = settings.change_settings(public, post)
					return settings.return_interface(public, result[0], result[1])
		if len(get) > 0:
			if get[0] == 'clear_ip':
				settings.clear_ip_blacklist(public)
				msg = 'IP blacklist cleared'
				return settings.return_interface(public, msg, 'green')
		return settings.return_interface(public)
	
	@staticmethod
	def change_settings(public, post):
		post_data = {}
		for key in post:
			if len(post[key]) > 0:
				post_data[key] = post[key]
		post_data = post
		if 'server' in post:
			public['database'].set('server', post['server'])
		if 'password_1' in post:
			if len(post['password_1']) > 0:
				if post['password_1'] == post['password_2']:
					password_hash = hashlib.sha512(post['password_1'].encode('utf-8')).hexdigest()
					public['database'].set('password', password_hash)
				else:
					return 'Passwords not match', 'red'
		if 'web_interface_port' in post:
			if post['web_interface_port'].isdigit():
				if int(post['web_interface_port']) != public['database'].get('web_interface_port'):
					public['database'].set('web_interface_port', int(post['web_interface_port']))
			else:
				return 'Port should contain only digits', 'red'
		if 'TLS' in post and post['TLS'] == 'on':
			public['database'].set('TLS', True)
		else:
			public['database'].set('TLS', False)
		if 'cert_path' in post:
			post['cert_path'] = urllib.parse.unquote(post['cert_path'])
			if post['cert_path'] != public['database'].get('cert_path'):
				if os.path.exists(post['cert_path']) or public['database'].get('TLS') == False:
					public['database'].set('cert_path', post['cert_path'])
				else:
					return 'Certificate file not found', 'red'
		if 'key_path' in post:
			post['key_path'] = urllib.parse.unquote(post['key_path'])
			if post['key_path'] != public['database'].get('key_path'):
				if os.path.exists(post['key_path']) or public['database'].get('TLS') == False:
					public['database'].set('key_path', post['key_path'])
				else:
					return 'Key file not found', 'red'
		return 'Settings saved','green'
	
	@staticmethod
	def clear_ip_blacklist(public):
		public['database'].set('IP', [])
	
	@staticmethod
	def return_interface(public, msg='', color='white'):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{msg_color}}', color)
			html = html.replace('{{msg}}', msg)
			html = html.replace('{{web_interface_port}}', str(public['database'].get('web_interface_port')))
			html = html.replace('{{TLS}}', 'checked' if public['database'].get('TLS') else '')
			html = html.replace('{{cert_path}}', public['database'].get('cert_path'))
			html = html.replace('{{key_path}}', public['database'].get('key_path'))
			return 200, html