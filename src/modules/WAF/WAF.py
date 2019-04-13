from scapy.all import *
from threading import Thread
import re
import urllib

class WAF():
	
	thread = None
	
	@staticmethod
	def install_entrypoint(public):
		public['database'].set('waf_state', 'off')
	
	@staticmethod
	def uninstall_entrypoint(public):
		public['database'].rem('waf_state')
	
	@staticmethod
	def startup_entrypoint(public):
		if public['database'].get('waf_state') == 'on':
			WAF.start(public)
			print('ok')
	
	@staticmethod
	def start(public):
		WAF.SQLI_pattern = re.compile(r"'\s*(AND|OR|XOR|&&|\|\|)\s*('|[0-9]|`?[a-z\._-]+`?\s*=|[a-z]+\s*\()")
		WAF.XSS_pattern = re.compile(r"(\b)(on\S+)(\s*)=|javascript|(<\s*)(\/*)script")
		WAF.thread = Thread(target = WAF.analyser, args=[public])
		WAF.thread.daemon = True
		WAF.thread.start()
		public['database'].set('waf_state', 'on')
	
	@staticmethod
	def stop(public):
		if WAF.thread != None:
			WAF.thread = None
		public['database'].set('waf_state', 'off')
	
	@staticmethod
	def analyser(public):
		WAF.public = public
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
	
	@staticmethod
	def check_XSS(packet):
		try:
			payload = bytes(packet[TCP].payload)
			if sum(payload) == 0:
				return
			load = str(payload)
			data = urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(load))))
			if WAF.XSS_pattern.search(data):
				WAF.public['report_ip'](packet[IP].src, 3, 'Cross-site scripting')
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
				WAF.public['report_ip'](packet[IP].src, 5, 'SQL injection')
		except:
			pass
	
	@staticmethod
	def web_entrypoint(public, get, post):
		if len(get) == 1 and 'start' in get:
			WAF.start(public)
		elif len(get) == 1 and 'stop' in get:
			WAF.stop(public)
		return WAF.return_interface(public)
	
	@staticmethod
	def return_interface(public):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{waf_state}}', public['database'].get('waf_state'))
			if public['database'].get('waf_state') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{waf_action}}', action)
			return 200, html
