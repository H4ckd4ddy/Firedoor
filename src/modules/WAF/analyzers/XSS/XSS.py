from config_database import database
from scapy.all import *
import urllib
from firedoor_modules_manager import modules_manager

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
				event = {}
				event['type'] = 'report_ip'
				event['data'] = {}
				event['data']['ip'] = packet[IP].src
				event['data']['level'] = 30
				event['data']['comment'] = 'Cross-site scripting'
				modules_manager.broadcast_event(event)	
		except:
			pass
