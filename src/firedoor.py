#!/usr/bin/env python3

###########################################
#                                         #
#               "Firedoor"                #
#                                         #
#             Etienne  SELLAN             #
#               2016->2019                #
#                                         #
###########################################

import sys
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import http.cookies
import signal
import json
import shutil
from shutil import copyfile
import hashlib
import time
from json_database import database
from firedoor_modules_manager import *

version = 4.0

# GLOBAL INIT BEGIN
public = {}
public['logs_path'] = '/var/log'
public['config_directory'] = '/etc/firedoor/'
public['session_timeout'] = 1800
public['database'] = None
public['sessions'] = {}
if hasattr(sys, '_MEIPASS'):
	public['base_directory'] = getattr(sys, '_MEIPASS', os.getcwd())
else:
	public['base_directory'] = os.path.dirname(os.path.realpath(__file__))
os.chdir(public['base_directory'])
# GLOBAL INIT END


def initialisation():
	public['database'] = database(public['config_directory']+'database.json')
	modules_manager.import_modules()

def install():
	if not os.path.isdir(public['config_directory']):
		os.mkdir(public['config_directory'])
	if not os.path.exists(public['config_directory']+'database.json'):
		copyfile('default_database.json', public['config_directory']+'database.json')
	initialisation()
	modules_manager.install_modules(public)
	
def uninstall():
	if confirm_uninstall():
		modules_manager.uninstall_modules(public)
		if os.path.isdir(public['config_directory']):
			shutil.rmtree(public['config_directory'])
		print('Firedoor successfully uninstalled !')

def confirm_uninstall():
	choice = ''
	while choice not in ['y', 'n']:
		choice = input('Uninstall Firedoor and delete all configurations [y/n] ? ').lower()
	if choice == 'y':
		return True
	else:
		print('/!\\ Uninstallation aborted /!\\')
















class request_handler(BaseHTTPRequestHandler):
	def parse_GET(self):
		parameters = self.path.split('/')
		parameters = list(filter(None, parameters))
		return parameters
	
	def do_GET(self):
		get = self.parse_GET()
		if self.check_auth():
			if len(get) > 0:
				if get[0] == 'icon' and len(get) == 2:
					self.return_module_image(get[1])
				if get[0] == 'logout' and len(get) == 1:
					public['sessions'][self.read_cookie('session')]['timestamp'] = 0
					self.return_html(200, '<script>document.location = "/";</script>')
				else:
					status, content = modules_manager.run_web_module(public, self, get[0], get[1:], {})
					self.return_html(status, content)
			else:
				self.return_html(200, self.return_homepage())
		elif len(get) > 0:
			self.return_html(403, '<script>document.location = "/";</script>')
		else:
			self.return_html(200, self.return_loginpage())
	
	def parse_POST(self):
		content_len = int(self.headers['content-length'])
		post_body = self.rfile.read(content_len)
		post_body = post_body.decode('utf-8')
		post_body = post_body.split('&')
		data = {}
		for var in post_body:
			var = var.split('=')
			name = var[0]
			value = var[1]
			data[name] = value
		return data
	
	def do_POST(self):
		parameters = self.parse_GET()
		post = self.parse_POST()
		if len(parameters) == 0 and len(post) > 0:
			if 'action' in post:
				if post['action'] == 'login':
					if hashlib.sha512(post['password'].encode('utf-8')).hexdigest() == public['database'].get('password'):
						token = os.urandom(32).hex()
						public['sessions'][token] = {}
						public['sessions'][token]['timestamp'] = time.time()
						session_cookie = 'session={}'.format(token)
						self.return_html(200, '<script>location.reload();</script>', session_cookie)
					else:
						self.return_html(200, self.return_loginpage().replace('<!---->', 'Access denied'))
						return
			self.return_html(200, self.return_loginpage())
		elif self.check_auth():
			status, content = modules_manager.run_web_module(public, self, parameters[0], parameters[1:], post)
			self.return_html(status, content)
		else:
			self.return_html(200, 'Access denied')

	def check_auth(self):
		if self.read_cookie('session') in public['sessions']:
			session_token = self.read_cookie('session')
			if public['sessions'][session_token]['timestamp'] > (time.time() - public['session_timeout']):
				return True
			else:
				del public['sessions'][session_token]
		return False

	def read_cookie(self, cookie_name):
		cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
		if cookie_name in cookies:
			return cookies[cookie_name].value
		return None

	def return_html(self, status, content, cookie_to_set=None):
		if not isinstance(status, int):
			status = 500
		self.send_response(status)
		self.send_header('Content-type', 'text/html; charset=UTF-8')
		if cookie_to_set != None:
			cookie_data = cookie_to_set.split('=')
			cookie = http.cookies.SimpleCookie()
			cookie[cookie_data[0]] = cookie_data[1]
			self.send_header("Set-Cookie", cookie.output(header='', sep=''))
		self.end_headers()
		content = content.replace('{{title}}', 'Firedoor v4.0 - {}'.format(public['database'].get('server')))
		content = content.replace('{{server_name}}', public['database'].get('server'))
		content = content.replace('{{firedoor_version}}', 'v'+str(version))
		self.wfile.write(content.encode('utf-8'))
		return

	def return_not_found(self, msg):
		html = '<meta http-equiv="refresh" content="2;URL=/">{}'.format(msg)
		self.return_html(404, html)
	
	def return_homepage(self):
		with open('html/home.html', 'r', encoding='utf-8') as homepage:
			modules_list = ''
			for module_name in modules_manager.modules:
				if hasattr(modules_manager.modules[module_name].obj, 'web_entrypoint'):
					if os.path.exists(modules_manager.modules[module_name].path+'/icon.png'):
						modules_list += '<a href="{}" title="{}"><div style="background: url(\'icon/{}\');background-size: cover;" class="icon"></div></a>'.format(module_name, module_name, module_name)
			html = homepage.read()
			html = html.replace('{{modules}}', modules_list)
			return html
		
	def return_loginpage(self):
		with open('html/login.html', 'r', encoding='utf-8') as loginpage:
			html = loginpage.read()
			return html

	def return_module_image(self, module_name):
		if module_name in modules_manager.modules:
			if hasattr(modules_manager.modules[module_name].obj, 'web_entrypoint'):
				if os.path.exists(modules_manager.modules[module_name].path+'/icon.png'):
					with open(modules_manager.modules[module_name].path+'/icon.png', 'rb') as image:
						self.send_response(200)
						self.send_header('Content-type', 'image/png')
						self.end_headers()
						shutil.copyfileobj(image, self.wfile)
				else:
					msg = 'Module "{}" does not have icon'.format(module_name)
					self.return_html(404, msg)
			else:
				msg = 'Module "{}" does not have web interface'.format(module_name)
				self.return_html(404, msg)
		else:
			msg = 'Module "{}" does no exist'.format(module_name)
			self.return_html(404, msg)






def run_on():
	print('\n')
	print('/-----------------------------------\\')
	print('|  Starting Firedoor on port {}  |'.format(str(public['database'].get('web_interface_port')).rjust(5, ' ')))
	print('\\-----------------------------------/')
	print('\n')
	server_address = ('', public['database'].get('web_interface_port'))
	httpd = HTTPServer(server_address, request_handler)
	if public['database'].get('TLS'):
		if os.path.exists(public['database'].get('cert_path')) and os.path.exists(public['database'].get('key_path')):
			httpd.socket = ssl.wrap_socket (httpd.socket, 
											keyfile=public['database'].get('key_path'), 
											certfile=public['database'].get('cert_path'),
											server_side=True)
	httpd.serve_forever()
	
def start_server():
	server = Thread(target=run_on)
	server.daemon = True
	server.start()
	signal.pause()
	
def main():
	if os.path.exists(public['config_directory']+'database.json'):
		initialisation()
	else:
		try:
			if sys.argv[1] == 'install':
				install()
				initialisation()
			else:
				raise Exception()
		except:
			print('Firedoor is not correctly installed')
			exit()
	if len(sys.argv) > 1:
		if sys.argv[1] == 'uninstall':
			uninstall()
		elif sys.argv[1] != 'install':
			modules_manager.run_cli_module(public, sys.argv[1], sys.argv[2:])
	else:
		modules_manager.startup_modules(public)
		start_server()

if __name__ == '__main__':
	main()