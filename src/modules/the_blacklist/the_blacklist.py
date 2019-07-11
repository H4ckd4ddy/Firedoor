import json
#import pyptables
import time
import threading
from threading import Thread
from config_database import database
from firedoor_modules_manager import modules_manager

class the_blacklist():
	
	thread = None
	
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
		
		def is_valid(self):
			if (time.time() < (self.timestamp + (database.get('period', 'blacklist')*3600))):
				return True
			else:
				return False
		
		def keep_stored(self):
			if time.time() < (self.timestamp + database.get('storage_time', 'blacklist')*3600):
				return True
			else:
				return False
	
	class ip:
		
		def __init__(self, addr):
			self.facts = []
			self.status = 'active'
			self.blocked_timestamp = 0
			self.ip_address = addr
		
		def add_fact(self, score, comment):
			self.facts.append(the_blacklist.fact(score, comment))
		
		def get_score(self):
			total = 0
			for fact in self.facts:
				if fact.is_valid():
					total += fact.score
			return total
		
		def check_score(self):
			if self.status == 'blocked':
				if time.time() > (self.blocked_timestamp + database.get('ban_duration', 'blacklist')*3600):
					self.status == 'active'
			else:
				if self.get_score() >= database.get('ban_score', 'blacklist'):
					self.block()
		
		def block(self):
			"""iptables = pyptables.Iptables()
			rule = pyptables.Rule(
									chain='INPUT',
									position='top',
									action='DROP',
									src=self.ip_address,
									comment='IP blocked'
								)
			iptables.add(rule)
			iptables.commit()"""
			self.blocked_timestamp = time.time()
			self.status = 'blocked'
			the_blacklist.export_blocklist()
		
		def to_list(self):
			data = {}
			data['addr'] = self.ip_address
			data['status'] = self.status
			data['score'] = self.get_score()
			return data
		
		def get_facts(self):
			result = []
			for f in self.facts:
				if f.keep_stored():
					result.append(f.to_list())
				else:
					del self.facts[f]
			return result
	
	ip_list = {}
	
	@classmethod
	def startup_entrypoint(cls):
		database.set('ban_score', 100, 'blacklist')
		database.set('period', 1, 'blacklist')  # in hours
		database.set('storage_time', 500, 'blacklist')  # in hours
		database.set('ban_duration', 24, 'blacklist')  # in hours
		cls.thread = Thread(target = cls.set_interval, args=[cls.check_banned, 3600])
		cls.thread.daemon = True
		cls.thread.start()
	
	@classmethod
	def event_listener(cls, event):
		if event['type'] == 'report_ip':
			cls.report_ip(event['data']['ip'], event['data']['level'], event['data']['comment'])
	
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
			cls.ip_list[addr] = cls.ip(addr)
		cls.ip_list[addr].add_fact(level, comment)
		cls.ip_list[addr].check_score()
	
	@classmethod
	def set_interval(cls, func, time):
		cls.thread.stop = False
		e = threading.Event()
		while not e.wait(time):
			if not cls.thread:
				exit
			elif cls.thread.stop:
				exit()
			else:
				func()
	
	@classmethod
	def check_banned(cls):
		event = {}
		event['type'] = 'reload_rules'
		modules_manager.broadcast_event(event)
		for i in cls.ip_list:
			cls.ip_list[i].check_score()
	
	@classmethod
	def export_blocklist(cls):
		with open(database.get('config_directory')+'block_rules.conf', 'w') as blocklist_file:
			rules = []
			for i in cls.ip_list:
				if cls.ip_list[i].status == 'blocked':
					rule = [
						'-A',
						'INPUT',
						'-s',
						cls.ip_list[i].ip_address,
						'-j',
						'DROP'
					]
					rules.append(rule)
			block_rules = json.dumps(rules, indent=4)
			blocklist_file.write(block_rules)
		event = {}
		event['type'] = 'reload_rules'
		modules_manager.broadcast_event(event)
	
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