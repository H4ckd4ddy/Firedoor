import json
import pyptables
import time

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
	
	@staticmethod
	def startup_entrypoint(database):
		#public['report_ip'] = the_blacklist.report_ip
		print('ok')
	
	@staticmethod
	def web_entrypoint(database, get, post):
		if len(get) > 0:
			if get[0] == 'ip':
				if len(get) == 3:
					return 200, the_blacklist.manage_ip(get[1], get[2])
				elif len(get) == 2:
					if get[1] in the_blacklist.ip_list:
						return 200, json.dumps(the_blacklist.ip_list[get[1]].get_facts())
				return 200, json.dumps(the_blacklist.get_ip_list())
		return the_blacklist.return_interface(database)
	
	@staticmethod
	def manage_ip(ip, action):
		result = {}
		try:
			if action == 'block':
				the_blacklist.ip_list[ip].block()
			elif action == 'remove':
				del the_blacklist.ip_list[ip]
		except:
			result['status'] = 'error'
			result['msg'] = 'Unable to perfom action on IP'
		else:
			result['status'] = 'ok'
			result['msg'] = 'Action performed'
		
		return json.dumps(result)
	
	@staticmethod
	def get_ip_list():
		result = []
		for i in the_blacklist.ip_list:
			result.append(the_blacklist.ip_list[i].to_list())
		return result
	
	@staticmethod
	def report_ip(addr, level, comment):
		if addr not in the_blacklist.ip_list:
			the_blacklist.ip_list[addr] = the_blacklist.ip(addr)
		the_blacklist.ip_list[addr].add_fact(level, comment)
		if the_blacklist.ip_list[addr].get_score() >= 10:
			the_blacklist.ip_list[addr].block()
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html