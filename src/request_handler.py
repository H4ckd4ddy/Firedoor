import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import http.cookies
import hashlib
import time
import shutil
from shutil import copyfile

from config_database import database
from firedoor_modules_manager import *

sessions = {}

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
					sessions[self.read_cookie('session')]['timestamp'] = 0
					self.return_html(200, '<script>document.location = "/";</script>')
				else:
					status, content = modules_manager.run_web_module(self, get[0], get[1:], {})
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
				if post['action'] == 'login' and 'password' in post:
					if hashlib.sha512(post['password'].encode('utf-8')).hexdigest() == database.get('password'):
						token = os.urandom(32).hex()
						sessions[token] = {}
						sessions[token]['timestamp'] = time.time()
						session_cookie = 'session={}'.format(token)
						self.return_html(200, '<script>location.reload();</script>', session_cookie)
					else:
						database.runtime_space['report_ip'](self.client_address[0], 2, 'Firedoor login attempt')
						self.return_html(200, self.return_loginpage().replace('<!---->', 'Access denied'))
						return
			self.return_html(200, self.return_loginpage())
		elif self.check_auth():
			status, content = modules_manager.run_web_module(self, parameters[0], parameters[1:], post)
			self.return_html(status, content)
		else:
			self.return_html(200, 'Access denied')

	def check_auth(self):
		if self.read_cookie('session') in sessions:
			session_token = self.read_cookie('session')
			if sessions[session_token]['timestamp'] > (time.time() - database.get('session_timeout')):
				return True
			else:
				del sessions[session_token]
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
		content = content.replace('{{title}}', 'Firedoor v4.0 - {}'.format(database.get('server')))
		content = content.replace('{{server_name}}', database.get('server'))
		content = content.replace('{{firedoor_version}}', 'v'+str(database.get('firedoor_version')))
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