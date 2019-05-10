from scapy.all import *
from threading import Thread
from config_database import database

class DNS_shield():
	
	thread = None
	
	@classmethod
	def install_entrypoint(cls):
		database.set('state', 'off', 'DNS_shield')
	
	@classmethod
	def uninstall_entrypoint(cls):
		database.rem('state', 'DNS_shield')
	
	@classmethod
	def startup_entrypoint(cls):
		if database.get('state', 'DNS_shield') == 'on':
			cls.start()
			print('ok')
	
	@classmethod
	def start(cls):
		cls.thread = Thread(target = cls.analyser)
		cls.thread.daemon = True
		cls.thread.start()
		database.set('state', 'on', 'DNS_shield')
	
	@classmethod
	def stop(cls):
		if cls.thread != None:
			cls.thread = None
		database.set('state', 'off', 'DNS_shield')
	
	@classmethod
	def analyser(cls):
		sniff(prn=cls.packet_callback, store=0, count=0, stop_filter=cls.check_state)
	
	@classmethod
	def check_state(cls, packet):
		if cls.thread == None:
			return True
		else:
			return False
	
	@classmethod
	def packet_callback(cls, packet):
		if UDP in packet:
			if packet[UDP].payload:
				if IP in packet:
					if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
						cls.check_dns_request(packet)
	
	@classmethod
	def check_dns_request(cls, packet):
		cls.check_for_any_request(packet)
	
	@classmethod
	def check_for_any_request(cls, packet):
		query_type = packet.getlayer(DNS).qd.fields['qtype']
		if query_type == 255:
			print('ANY request detected !!!')
			database.runtime_space['report_ip'](packet[IP].src, 3, 'Any request DNS')
		else:
			print('Normal request')
	
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
			html = html.replace('{{DNS_shield_state}}', database.get('state', 'DNS_shield'))
			if database.get('state', 'DNS_shield') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{DNS_shield_action}}', action)
			return 200, html