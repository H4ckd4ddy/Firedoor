from config_database import database
from scapy.all import *
import urllib
import re

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
				database.runtime_space['report_ip'](packet[IP].src, 5, 'SQL injection')
		except:
			pass
