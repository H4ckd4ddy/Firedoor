from scapy.all import *
from threading import Thread
import re
import urllib
from analyzers_manager import analyzers_manager

class WAF():
	
	thread = None
	analyzers = {}
	
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
		WAF.SQLI_pattern = re.compile(r"'\s*(AND|OR|XOR|&&|\|\|)\s*('|[0-9]|`?[a-z\._-]+`?\s*=|[a-z]+\s*\()")
		WAF.XSS_pattern = re.compile(r"(\b)(on\S+)(\s*)=|javascript|(<\s*)(\/*)script")
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
		sniff(prn=WAF.packet_callback, store=0, count=0, stop_filter=WAF.check_state)
		#sniff(filter='tcp', prn=WAF.packet_callback, store=0, count=0, stop_filter=WAF.check_state)
	
	@staticmethod
	def check_state(packet):
		if WAF.thread == None:
			return True
		else:
			return False
	
	@staticmethod
	def packet_callback(packet):
		if TCP in packet:
			if packet[TCP].payload:
				if packet[IP].dport == 8080:
					WAF.check_packet(packet)
	
	@staticmethod
	def check_packet(packet):
		WAF.check_XSS(packet)
		WAF.check_SQLI(packet)
	
	"""
	@staticmethod
	def import_analyzers():
		if os.path.isdir('analyzers'):
			for analyzer_name in os.listdir('analyzers'):
				if analyzer_name not in WAF.analyzers:
					WAF.analyzers[analyzer_name] = module(directory, module_name)
	"""
	
	@staticmethod
	def check_XSS(packet):
		try:
			payload = bytes(packet[TCP].payload)
			if sum(payload) == 0:
				return
			load = str(payload)
			data = urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(load))))
			if WAF.XSS_pattern.search(data):
				WAF.database.runtime_space['report_ip'](packet[IP].src, 3, 'Cross-site scripting')
		except:
			pass
	
	@staticmethod
	def check_SQLI(packet):
		try:
			payload = bytes(packet[TCP].payload)
			if sum(payload) == 0:
				return
			load = str(payload)
			data = urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(load))))
			if WAF.SQLI_pattern.search(data):
				WAF.database.report_ip(packet[IP].src, 5, 'SQL injection')
		except:
			pass
	
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
			if database.get('waf_state') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{waf_action}}', action)
			return 200, html
