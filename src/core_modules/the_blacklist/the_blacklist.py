import json
import pyptables
import time
from config_database import database

class the_blacklist():
	
	class fact:
		timestamp = None
		comment = None
		score = 0
		def __init__(self, score, comment):
			self.timestamp = time.time()
			self.score = score
			self.comment = comment
		
		def to_list(self):
			data = {}
			data['timestamp'] = self.timestamp
			data['score'] = self.score
			data['comment'] = self.comment
			return data
	
	class ip:
		ip_address = None
		facts = []
		status = 'active'
		def __init__(self, addr):
			self.ip_address = addr
		
		def add_fact(self, score, comment):
			self.facts.append(the_blacklist.fact(score, comment))
		
		def get_score(self):
			total = 0
			for fact in self.facts:
				total += fact.score
			return total
		
		def block(self):
			iptables = pyptables.Iptables()
			rule = pyptables.Rule(
									chain='INPUT',
									position='top',
									action='DROP',
									src=self.ip_address,
									comment='IP blocked'
								)
			iptables.add(rule)
			iptables.commit()
			self.status = 'blocked'
		
		def to_list(self):
			data = {}
			data['addr'] = self.ip_address
			data['status'] = self.status
			data['score'] = self.get_score()
			return data
		
		def get_facts(self):
			result = []
			for f in self.facts:
				result.append(f.to_list())
			return result
	
	ip_list = {}
	
	@classmethod
	def startup_entrypoint(cls):
		database.runtime_space['report_ip'] = cls.report_ip
	
	@classmethod
	def web_entrypoint(cls, client_ip, get, post):
		if len(get) > 0:
			if get[0] == 'ip':
				if len(get) == 3:
					return 200, cls.manage_ip(get[1], get[2])
				elif len(get) == 2:
					if get[1] in the_blacklist.ip_list:
						return 200, json.dumps(cls.ip_list[get[1]].get_facts())
				return 200, json.dumps(cls.get_ip_list())
			elif get[0] == 'settings_page':
				return cls.return_settings_page()
			
			if len(get) == 2:
				if get[0] == 'settings':
					setting_value = database.get(get[1], 'the_blacklist')
					if setting_value:
						return 200, json.dumps(setting_value)
					else:
						return 404, 'setting not found'
		return cls.return_interface()
	
	@classmethod
	def manage_ip(cls, ip, action):
		result = {}
		try:
			if action == 'block':
				cls.ip_list[ip].block()
			elif action == 'remove':
				del cls.ip_list[ip]
		except:
			result['status'] = 'error'
			result['msg'] = 'Unable to perfom action on IP'
		else:
			result['status'] = 'ok'
			result['msg'] = 'Action performed'
		
		return json.dumps(result)
	
	@classmethod
	def get_ip_list(cls):
		result = []
		for i in cls.ip_list:
			result.append(cls.ip_list[i].to_list())
		return result
	
	@classmethod
	def report_ip(cls, addr, level, comment):
		if addr not in cls.ip_list:
			cls.ip_list[addr] = the_blacklist.ip(addr)
		cls.ip_list[addr].add_fact(level, comment)
		if cls.ip_list[addr].get_score() >= 10:
			cls.ip_list[addr].block()
	
	@classmethod
	def return_settings_page(cls):
		with open('settings.html', 'r') as interface:
			html = interface.read()
			return 200, html
	
	@classmethod
	def return_interface(cls):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html