import time
import threading
from threading import Thread
import signal
import os
import shutil
import psutil
import datetime
import netifaces
from config_database import database

class monitoring():
	
	data = {}
	thread = None
	
	@classmethod
	def install_entrypoint(cls):
		database.set('state', 'off', 'monitoring')
		database.set('logs_dir', '/var/log/firedoor/', 'monitoring')
	
	@classmethod
	def uninstall_entrypoint(cls):
		database.rem('state', 'monitoring')
		if os.path.isdir(database.get('logs_dir', 'monitoring')):
			shutil.rmtree(database.get('logs_dir', 'monitoring'))
	
	@classmethod
	def startup_entrypoint(cls):
		if database.get('state', 'monitoring') == 'on':
			cls.start(60)
	
	@classmethod
	def web_entrypoint(cls, client_ip, get, post):
		if len(get) == 1 and 'start' in get:
			cls.start(60)
		elif len(get) == 1 and 'stop' in get:
			cls.stop()
		elif 'logs' in get:
			if len(get) == 2:
				return cls.return_logs(get[1])
			elif len(get) == 3:
				return cls.return_logs(get[1], get[2])
		return cls.return_interface()
	
	@classmethod
	def start(cls, interval):
		cls.thread = Thread(target = cls.set_interval, args=[cls.measuring_values, interval])
		cls.thread.daemon = True
		cls.thread.start()
		database.set('state', 'on', 'monitoring')
	
	@classmethod
	def stop(cls):
		if cls.thread != None:
			cls.thread.stop = True
			cls.thread = None
		database.set('state', 'off', 'monitoring')
	
	@classmethod
	def measuring_values(cls):
		cls.prepare_directory()
		measuring_types = ['CPU', 'RAM', 'NET']
		for measuring_type in measuring_types:
			cls.append_to_logs(measuring_type, cls.measuring(measuring_type))
	
	@classmethod
	def measuring(cls, measuring_type):
		values = []
		if measuring_type == 'CPU':
			values.append(str(psutil.cpu_percent()))
		elif measuring_type == 'RAM':
			ram_values = dict(psutil.virtual_memory()._asdict())
			values.append(str(ram_values['total']))
			values.append(str(ram_values['used']))
		elif measuring_type == 'NET':
			interface = next(iter(netifaces.gateways()['default'].values()))[1]
			net_values = dict(psutil.net_io_counters(pernic=True)[interface]._asdict())
			net_values_time = time.time()
			if 'last_net_value' in monitoring.data:
				net_values_2 = net_values
				net_values_time_2 = net_values_time
				net_values = monitoring.data['last_net_value']['values']
				net_values_time = monitoring.data['last_net_value']['timestamp']
			else:
				time.sleep(1)
				net_values_2 = dict(psutil.net_io_counters(pernic=True)[interface]._asdict())
				net_values_time_2 = time.time()
			interval = (net_values_time_2 - net_values_time)
			download = round((net_values_2['bytes_recv'] - net_values['bytes_recv']) / interval)
			upload = round((net_values_2['bytes_sent'] - net_values['bytes_sent']) / interval)
			
			monitoring.data['last_net_value'] = {}
			monitoring.data['last_net_value']['values'] = net_values_2
			monitoring.data['last_net_value']['timestamp'] = net_values_time_2
			
			values.append(str(download))
			values.append(str(upload))
		return values
	
	@classmethod
	def append_to_logs(cls, mesuring_type, values):
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		time = datetime.datetime.now().strftime('%H:%M:%S')
		value = ' , '.join(values)
		with open(database.get('logs_dir', 'monitoring')+date+'/'+mesuring_type+'.log', 'a+') as logs_file:
			logs_file.write('{} {} , {}\n'.format(date, time, value))
	
	@classmethod
	def prepare_directory(cls):
		if not os.path.isdir(database.get('logs_dir', 'monitoring')):
			os.mkdir(database.get('logs_dir', 'monitoring'))
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		if not os.path.isdir(database.get('logs_dir', 'monitoring')+date):
			os.mkdir(database.get('logs_dir', 'monitoring')+date)
	
	@classmethod
	def return_logs(cls, mesuring_type, date=datetime.datetime.now().strftime('%Y-%m-%d')):
		if os.path.exists(database.get('logs_dir', 'monitoring')+date+'/'+mesuring_type+'.log'):
			with open(database.get('logs_dir', 'monitoring')+date+'/'+mesuring_type+'.log', 'r') as logs_file:
				return 200, logs_file.read()
		return 404, 'Not found'
	
	@classmethod
	def generate_date_list(cls):
		if os.path.exists(database.get('logs_dir', 'monitoring')):
			dates = []
			for date in sorted(os.listdir(database.get('logs_dir', 'monitoring')), reverse=True):
				dates.append('<option>{}</option>'.format(date))
			return '\n'.join(dates)
		return 'no data'
	
	@classmethod
	def return_interface(cls):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{monitoring_dates}}', cls.generate_date_list())
			html = html.replace('{{monitoring_state}}', database.get('state', 'monitoring'))
			if database.get('state', 'monitoring') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{monitoring_action}}', action)
			return 200, html
	
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