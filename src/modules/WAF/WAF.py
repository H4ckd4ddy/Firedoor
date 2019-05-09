from scapy.all import *
from threading import Thread
import re
import urllib
from analyzers_manager import analyzers_manager

class WAF():
	
	thread = None
	
	@staticmethod
	def install_entrypoint(database):
		database.set('state', 'off', 'WAF')
	
	@staticmethod
	def uninstall_entrypoint(database):
		database.rem('state', 'WAF')
	
	@staticmethod
	def startup_entrypoint(database):
		if database.get('state', 'WAF') == 'on':
			WAF.start(database)
			print('ok')
	
	@staticmethod
	def start(database):
		analyzers_manager.import_analyzers()
		WAF.thread = Thread(target = WAF.analyser, args=[database])
		WAF.thread.daemon = True
		WAF.thread.start()
		database.set('state', 'on', 'WAF')
	
	@staticmethod
	def stop(database):
		if WAF.thread != None:
			WAF.thread = None
		database.set('state', 'off', 'WAF')
	
	@staticmethod
	def analyser(database):
		WAF.database = database
		sniff(prn=analyzers_manager.packets_handler, store=0, count=0, stop_filter=WAF.check_state)
	
	@staticmethod
	def check_state(packet):
		if WAF.thread == None:
			return True
		else:
			return False
	
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if len(get) == 1 and 'start' in get:
			WAF.start(database)
		elif len(get) == 1 and 'stop' in get:
			WAF.stop(database)
		return WAF.return_interface(database)
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{waf_state}}', database.get('state', 'WAF'))
			if database.get('state', 'WAF') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{waf_action}}', action)
			return 200, html