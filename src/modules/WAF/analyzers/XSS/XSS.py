from config_database import database
from scapy.all import *
import urllib

class XSS():
	
	XSS_pattern = re.compile(r"(\b)(on\S+)(\s*)=|javascript|(<\s*)(\/*)script")
	
	@classmethod
	def packet_entrypoint(cls, packet):
		try:
			payload = bytes(packet[TCP].payload)
			if sum(payload) == 0:
				return
			load = str(payload)
			data = urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(load))))
			if cls.XSS_pattern.search(data):
				database.runtime_space['report_ip'](packet[IP].src, 3, 'Cross-site scripting')
		except:
			pass
