import sys
import os
from scapy.all import *

class analyzer:

	obj = None
	path = None
	enable = True

	def __init__(self, directory, analyzer_name):
		if os.path.isdir(directory+'/'+analyzer_name):
			self.path = directory+'/'+analyzer_name
			sys.path.insert(0, self.path)
			analyzer = __import__(analyzer_name)
			self.obj = getattr(analyzer, analyzer_name)

class analyzers_manager:

	analyzers = {}

	@classmethod
	def import_analyzers(cls):
		directory = 'analyzers'
		if os.path.isdir(directory):
			for analyzer_name in sorted(os.listdir(directory)):
				if analyzer_name not in cls.analyzers:
					cls.analyzers[analyzer_name] = analyzer(directory, analyzer_name)

	@classmethod
	def packets_handler(cls, packet):
		if TCP in packet:
			if packet[TCP].payload:
				if packet[IP].dport == 80:
					cls.analyse(packet)

	@classmethod
	def analyse(cls, packet):
		for analyzer_name in cls.analyzers:
			if cls.analyzers[analyzer_name].enable:
				cls.analyzers[analyzer_name].obj.packet_entrypoint(packet)