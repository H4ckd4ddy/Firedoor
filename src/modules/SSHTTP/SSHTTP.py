from threading import Thread
import subprocess
#import envoy
import signal
import os

#def signal_handler(sig, frame):
#	print('nothing...')
#signal.signal(signal.SIGINT, signal_handler)
#signal.signal(signal.SIGTERM, signal_handler)
#signal.signal(signal.SIGQUIT, signal_handler)
#signal.signal(signal.SIGHUP, signal_handler)
#signal.signal(signal.SIGTRAP, signal_handler)

#catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
#for sig in catchable_sigs:
#    signal.signal(sig, signal_handler)

class SSHTTP():
	
	"""
	@staticmethod
	def web_entrypoint(database, client_ip, get, post):
		if len(post) > 0:
			if 'command' in post:
				# ----- PROBLEM BEGIN -----
				print(SSHTTP.exec_cmd('echo test'))
				print('ok')
				return 200, 'ok'
				# ------ PROBLEM END ------
		else:
			return SSHTTP.return_interface(database)
	"""
	
	@staticmethod
	def return_command_result(cmd):
		thread = Thread(target = SSHTTP.exec_command)
		thread.start()
		#thread.join()
		return 200, 'html'

	@staticmethod
	def cli_entrypoint(database, args):
		print(SSHTTP.exec_cmd('echo test'))

	@staticmethod
	def exec_cmd(cmd):
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		result = p.communicate()[0].decode("utf-8")
		result = str(result)
		return result
	
	@staticmethod
	def return_interface(database):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html