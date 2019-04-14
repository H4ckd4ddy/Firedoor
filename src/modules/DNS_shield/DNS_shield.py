from scapy.all import *
from threading import Thread

class DNS_shield():
	
	thread = None
	
	@staticmethod
	def install_entrypoint(database):
		database.set('dns_shield_state', 'off')
	
	@staticmethod
	def uninstall_entrypoint(database):
		database.rem('dns_shield_state')
	
	@staticmethod
	def startup_entrypoint(database):
		if database.get('dns_shield_state') == 'on':
			DNS_shield.start(database)
			print('ok')
	
	@staticmethod
	def start(database):
		DNS_shield.thread = Thread(target = DNS_shield.analyser, args=[database])
		DNS_shield.thread.daemon = True
		DNS_shield.thread.start()
		database.set('dns_shield_state', 'on')
	
	@staticmethod
	def stop(database):
		if DNS_shield.thread != None:
			DNS_shield.thread = None
		database.set('dns_shield_state', 'off')
	
	@staticmethod
	def analyser(database):
		DNS_shield.database = database
		sniff(prn=DNS_shield.packet_callback, store=0, count=0, stop_filter=DNS_shield.check_state)
	
	@staticmethod
	def check_state(packet):
		if DNS_shield.thread == None:
			return True
		else:
			return False
	
	@staticmethod
	def packet_callback(packet):
		if UDP in packet:
			if packet[UDP].payload:
				if IP in packet:
					if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
						DNS_shield.check_dns_request(packet)
	
	@staticmethod
	def check_dns_request(packet):
		DNS_shield.check_for_any_request(packet)
	
	@staticmethod
	def check_for_any_request(packet):
		query_type = packet.getlayer(DNS).qd.fields['qtype']
		if query_type == 255:
			print('ANY request detected !!!')
			DNS_shield.database.report_ip(packet[IP].src, 3, 'Any request DNS')
		else:
			print('Normal request')
	
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if len(get) == 1 and 'start' in get:
			DNS_shield.start(database)
		elif len(get) == 1 and 'stop' in get:
			DNS_shield.stop(database)
		return 200, 'OK'
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html