import time
import threading
from threading import Thread
import signal
import os
import shutil
import psutil
import datetime
import netifaces

class monitoring():
	
	data = {}
	thread = None
	
	@staticmethod
	def install_entrypoint(database):
		database.set('state', 'off', 'monitoring')
		database.set('logs_dir', '/var/log/firedoor/', 'monitoring')
	
	@staticmethod
	def uninstall_entrypoint(database):
		database.rem('state', 'monitoring')
		if os.path.isdir(database.get('logs_dir', 'monitoring')):
			shutil.rmtree(database.get('logs_dir', 'monitoring'))
	
	@staticmethod
	def startup_entrypoint(database):
		if database.get('state', 'monitoring') == 'on':
			monitoring.start(database, 60)
	
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if len(get) == 1 and 'start' in get:
			monitoring.start(database, 60)
		elif len(get) == 1 and 'stop' in get:
			monitoring.stop(database)
		elif 'logs' in get:
			if len(get) == 2:
				return monitoring.return_logs(database, get[1])
			elif len(get) == 3:
				return monitoring.return_logs(database, get[1], get[2])
		return monitoring.return_interface(database)
	
	@staticmethod
	def start(database, interval):
		monitoring.thread = Thread(target = monitoring.set_interval, args=[database, monitoring.measuring_values, interval])
		monitoring.thread.daemon = True
		monitoring.thread.start()
		database.set('state', 'on', 'monitoring')
	
	@staticmethod
	def stop(database):
		if monitoring.thread != None:
			monitoring.thread.stop = True
			monitoring.thread = None
		database.set('state', 'off', 'monitoring')
	
	@staticmethod
	def measuring_values(database):
		monitoring.prepare_directory(database)
		measuring_types = ['CPU', 'RAM', 'NET']
		for measuring_type in measuring_types:
			monitoring.append_to_logs(database, measuring_type, monitoring.measuring(measuring_type))
	
	@staticmethod
	def measuring(measuring_type):
		values = []
		if measuring_type == 'CPU':
			values.append(str(psutil.cpu_percent()))
			#values.append(str(0)) #tmp
		elif measuring_type == 'RAM':
			ram_values = dict(psutil.virtual_memory()._asdict())
			#values.append(str(0)) #tmp
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
			#values.append(str(0)) #tmp
		return values
	
	@staticmethod
	def append_to_logs(database, mesuring_type, values):
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		time = datetime.datetime.now().strftime('%H:%M:%S')
		value = ' , '.join(values)
		with open(database.get('logs_dir', 'monitoring')+date+'/'+mesuring_type+'.log', 'a+') as logs_file:
			logs_file.write('{} {} , {}\n'.format(date, time, value))
	
	@staticmethod
	def prepare_directory(database):
		if not os.path.isdir(database.get('logs_dir', 'monitoring')):
			os.mkdir(database.get('logs_dir', 'monitoring'))
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		if not os.path.isdir(database.get('logs_dir', 'monitoring')+date):
			os.mkdir(database.get('logs_dir', 'monitoring')+date)
	
	@staticmethod
	def return_logs(database, mesuring_type, date=datetime.datetime.now().strftime('%Y-%m-%d')):
		if os.path.exists(database.get('logs_dir', 'monitoring')+date+'/'+mesuring_type+'.log'):
			with open(database.get('logs_dir', 'monitoring')+date+'/'+mesuring_type+'.log', 'r') as logs_file:
				return 200, logs_file.read()
		return 404, 'Not found'
	
	@staticmethod
	def generate_date_list(database):
		if os.path.exists(database.get('logs_dir', 'monitoring')):
			dates = []
			for date in sorted(os.listdir(database.get('logs_dir', 'monitoring')), reverse=True):
				dates.append('<option>{}</option>'.format(date))
			return '\n'.join(dates)
		return 'no data'
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{monitoring_dates}}', monitoring.generate_date_list(database))
			html = html.replace('{{monitoring_state}}', database.get('state', 'monitoring'))
			if database.get('state', 'monitoring') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{monitoring_action}}', action)
			return 200, html
	
	@staticmethod
	def set_interval(database, func, time):
		monitoring.thread.stop = False
		e = threading.Event()
		while not e.wait(time):
			if not monitoring.thread:
				exit
			elif monitoring.thread.stop:
				exit()
			else:
				func(database)