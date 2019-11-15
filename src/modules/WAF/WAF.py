from scapy.all import *
from threading import Thread
import re
import urllib
from analyzers_manager import analyzers_manager
from config_database import database

class WAF():
	
	thread = None
	
	@classmethod
	def install_entrypoint(cls):
		database.set('state', 'off', 'WAF')
	
	@classmethod
	def uninstall_entrypoint(cls):
		database.rem('state', 'WAF')
	
	@classmethod
	def startup_entrypoint(cls):
		if database.get('state', 'WAF') == 'on':
			cls.start()
			print('ok')
	
	@classmethod
	def start(cls):
		analyzers_manager.import_analyzers()
		cls.thread = Thread(target = cls.analyser)
		cls.thread.daemon = True
		cls.thread.start()
		database.set('state', 'on', 'WAF')
	
	@classmethod
	def stop(cls):
		if cls.thread != None:
			cls.thread = None
		database.set('state', 'off', 'WAF')
	
	@classmethod
	def analyser(cls):
		sniff(prn=analyzers_manager.packets_handler, store=0, count=0, stop_filter=cls.check_state)
	
	@classmethod
	def check_state(cls, packet):
		if cls.thread == None:
			return True
		else:
			return False
	
	@classmethod
	def web_entrypoint(cls, client_ip, get, post):
		if len(get) == 1 and 'start' in get:
			cls.start()
		elif len(get) == 1 and 'stop' in get:
			cls.stop()
		return cls.return_interface()
	
	@classmethod
	def return_interface(cls):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{waf_state}}', database.get('state', 'WAF'))
			if database.get('state', 'WAF') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{waf_action}}', action)
			return 200, html