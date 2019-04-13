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
	def install_entrypoint(public):
		public['database'].set('monitoring_state', 'off')
		public['database'].set('monitoring_logs_dir', '/var/log/firedoor/')
	
	@staticmethod
	def uninstall_entrypoint(public):
		public['database'].rem('monitoring_state')
		if os.path.isdir(public['database'].get('monitoring_logs_dir')):
			shutil.rmtree(public['database'].get('monitoring_logs_dir'))
	
	@staticmethod
	def startup_entrypoint(public):
		if public['database'].get('monitoring_state') == 'on':
			monitoring.start(public, 60)
	
	@staticmethod
	def web_entrypoint(public, get, post):
		if len(get) == 1 and 'start' in get:
			monitoring.start(public, 60)
		elif len(get) == 1 and 'stop' in get:
			monitoring.stop(public)
		elif 'logs' in get:
			if len(get) == 2:
				return monitoring.return_logs(public, get[1])
			elif len(get) == 3:
				return monitoring.return_logs(public, get[1], get[2])
		return monitoring.return_interface(public)
	
	@staticmethod
	def start(public, interval):
		monitoring.thread = Thread(target = monitoring.set_interval, args=[public, monitoring.measuring_values, interval])
		monitoring.thread.daemon = True
		monitoring.thread.start()
		public['database'].set('monitoring_state', 'on')
	
	@staticmethod
	def stop(public):
		if monitoring.thread != None:
			monitoring.thread.stop = True
			monitoring.thread = None
		public['database'].set('monitoring_state', 'off')
	
	@staticmethod
	def measuring_values(public):
		monitoring.prepare_directory(public)
		measuring_types = ['CPU', 'RAM', 'NET']
		for measuring_type in measuring_types:
			monitoring.append_to_logs(public, measuring_type, monitoring.measuring(measuring_type))
	
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
	def append_to_logs(public, mesuring_type, values):
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		time = datetime.datetime.now().strftime('%H:%M:%S')
		value = ' , '.join(values)
		with open(public['database'].get('monitoring_logs_dir')+date+'/'+mesuring_type+'.log', 'a+') as logs_file:
			logs_file.write('{} {} , {}\n'.format(date, time, value))
	
	@staticmethod
	def prepare_directory(public):
		if not os.path.isdir(public['database'].get('monitoring_logs_dir')):
			os.mkdir(public['database'].get('monitoring_logs_dir'))
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		if not os.path.isdir(public['database'].get('monitoring_logs_dir')+date):
			os.mkdir(public['database'].get('monitoring_logs_dir')+date)
	
	@staticmethod
	def return_logs(public, mesuring_type, date=datetime.datetime.now().strftime('%Y-%m-%d')):
		if os.path.exists(public['database'].get('monitoring_logs_dir')+date+'/'+mesuring_type+'.log'):
			with open(public['database'].get('monitoring_logs_dir')+date+'/'+mesuring_type+'.log', 'r') as logs_file:
				return 200, logs_file.read()
		return 404, 'Not found'
	
	@staticmethod
	def generate_date_list(public):
		if os.path.exists(public['database'].get('monitoring_logs_dir')):
			dates = []
			for date in sorted(os.listdir(public['database'].get('monitoring_logs_dir')), reverse=True):
				dates.append('<option>{}</option>'.format(date))
			return '\n'.join(dates)
		return 'no data'
	
	@staticmethod
	def return_interface(public):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			html = html.replace('{{monitoring_dates}}', monitoring.generate_date_list(public))
			html = html.replace('{{monitoring_state}}', public['database'].get('monitoring_state'))
			if public['database'].get('monitoring_state') == 'on':
				action = 'stop'
			else:
				action = 'start'
			html = html.replace('{{monitoring_action}}', action)
			return 200, html
	
	@staticmethod
	def set_interval(public, func, time):
		monitoring.thread.stop = False
		e = threading.Event()
		while not e.wait(time):
			if not monitoring.thread:
				exit
			elif monitoring.thread.stop:
				exit()
			else:
				func(public)