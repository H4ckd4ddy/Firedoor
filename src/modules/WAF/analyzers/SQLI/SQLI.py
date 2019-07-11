from config_database import database
from scapy.all import *
import urllib
import re
from firedoor_modules_manager import modules_manager

class SQLI():
	
	SQLI_pattern = re.compile(r"'\s*(AND|OR|XOR|&&|\|\|)\s*('|[0-9]|`?[a-z\._-]+`?\s*=|[a-z]+\s*\()")
	
	@classmethod
	def packet_entrypoint(cls, packet):
		try:
			payload = bytes(packet[TCP].payload)
			if sum(payload) == 0:
				return
			load = str(payload)
			data = urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(load))))
			if cls.SQLI_pattern.search(data):
				event = {}
				event['type'] = 'report_ip'
				event['data'] = {}
				event['data']['ip'] = packet[IP].src
				event['data']['level'] = 50
				event['data']['comment'] = 'SQL injection'
				modules_manager.broadcast_event(event)
		except:
			pass
