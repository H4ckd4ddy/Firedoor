import os
import hashlib
import urllib.parse
from firedoor_modules_manager import *
from config_database import database

class settings():
	
	@classmethod
	def web_entrypoint(cls, client_ip, get, post):
		if len(post) > 0:
			if 'action' in post:
				if post['action'] == 'change_settings':
					result = settings.change_settings(post)
					return settings.return_interface(result[0], result[1])
		return settings.return_interface()
	
	@classmethod
	def change_settings(cls, post):
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
		for var_name in post:
			if var_name.find('hidden_activation__') >= 0:
				module_name = var_name.replace('hidden_activation__','')
				if module_name in modules_manager.modules:
					desirate_state = False
					if 'activation__{}'.format(module_name) in post:
						if post['activation__{}'.format(module_name)] == 'on':
							desirate_state = True
					if desirate_state != database.get('activated_modules')[module_name]:
						modules_manager.modules[module_name].change_state(desirate_state)
		return 'Settings saved','green'
	
	@classmethod
	def generate_modules_checklist(cls):
		modules = modules_manager.get_optional_modules_list()
		checklist = ''
		for module_name in modules:
			checklist += '<tr>\n'
			checklist += '<td>'+module_name+'</td>\n'
			check = 'checked' if modules[module_name] else ''
			checklist += '<td><input type="checkbox" name="activation__{}" {}></td>\n'.format(module_name, check)
			checklist += '<input type="hidden" name="hidden_activation__{}" value="disable">\n'.format(module_name, check)
			checklist += '</tr>\n'
		return checklist

	@classmethod
	def return_interface(cls, msg='', color='white'):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{msg_color}}', color)
			html = html.replace('{{msg}}', msg)
			html = html.replace('{{web_interface_port}}', str(database.get('web_interface_port')))
			html = html.replace('{{TLS}}', 'checked' if database.get('TLS') else '')
			html = html.replace('{{cert_path}}', database.get('cert_path'))
			html = html.replace('{{key_path}}', database.get('key_path'))
			html = html.replace('{{modules_checklist}}', settings.generate_modules_checklist())
			return 200, html