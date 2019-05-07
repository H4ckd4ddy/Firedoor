#!/usr/bin/env python3

###########################################
#                                         #
#               "Firedoor"                #
#                                         #
#             Etienne  SELLAN             #
#               2016->2019                #
#                                         #
###########################################

import sys
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import signal
import json
import shutil
from shutil import copyfile
from config_database import database
from firedoor_modules_manager import *
from request_handler import request_handler

version = 4.0

# GLOBAL INIT BEGIN
config_directory = "/etc/firedoor/"
# GLOBAL INIT END



def install():
	if not os.path.isdir(config_directory):
		os.mkdir(config_directory)
	if not os.path.exists(config_directory+'database.json'):
		if hasattr(sys, '_MEIPASS'):
			base_directory = getattr(sys, '_MEIPASS', os.getcwd())
		else:
			base_directory = os.path.dirname(os.path.realpath(__file__))
		os.chdir(base_directory)
		copyfile('default_database.json', config_directory+'database.json')
	if not os.path.exists('/etc/systemd/system/firedoor.service') and os.path.isdir('/etc/systemd/system'):
		with open('firedoor.service', 'r') as default_service_file:
			service = default_service_file.read()
			service = service.replace('{{firedoor_path}}', os.path.realpath(__file__))
			with open('/etc/systemd/system/firedoor.service', 'w+') as service_file:
				service_file.write(service)
		os.system('systemctl enable firedoor.service')
	initialisation()
	modules_manager.install_modules()

def initialisation():
	database.init(config_directory+'database.json')
	database.set('config_directory', config_directory)
	if hasattr(sys, '_MEIPASS'):
		database.set('base_directory', getattr(sys, '_MEIPASS', os.getcwd()))
	else:
		database.set('base_directory', os.path.dirname(os.path.realpath(__file__)))
	os.chdir(database.get('base_directory'))
	modules_manager.import_modules()

def uninstall():
	if confirm_uninstall():
		modules_manager.uninstall_modules()
		if os.path.isdir(config_directory):
			shutil.rmtree(config_directory)
		print('Firedoor successfully uninstalled !')

def confirm_uninstall():
	choice = ''
	while choice not in ['y', 'n']:
		choice = input('Uninstall Firedoor and delete all configurations [y/n] ? ').lower()
	if choice == 'y':
		return True
	else:
		print('/!\\ Uninstallation aborted /!\\')










def run_on():
	print('\n')
	print('/-----------------------------------\\')
	print('|  Starting Firedoor on port {}  |'.format(str(database.get('web_interface_port')).rjust(5, ' ')))
	print('\\-----------------------------------/')
	print('\n')
	server_address = ('', database.get('web_interface_port'))
	httpd = HTTPServer(server_address, request_handler)
	if database.get('TLS'):
		if os.path.exists(database.get('cert_path')) and os.path.exists(database.get('key_path')):
			httpd.socket = ssl.wrap_socket (httpd.socket, 
											keyfile=database.get('key_path'), 
											certfile=database.get('cert_path'),
											server_side=True)
	httpd.serve_forever()
	
def start_server():
	database.set('sessions', {})
	server = Thread(target=run_on)
	server.daemon = True
	server.start()
	signal.pause()
	
def main():
	if os.path.exists(config_directory+'database.json'):
		initialisation()
		if len(sys.argv) > 1:
			if sys.argv[1] == 'uninstall':
				uninstall()
			else:
				modules_manager.run_cli_module(sys.argv[1], sys.argv[2:])
		else:
			modules_manager.startup_modules()
			start_server()
	else:
		if len(sys.argv) > 1:
			if sys.argv[1] == 'install':
				install()
			else:
				print('Firedoor is not correctly installed')
				exit()

if __name__ == '__main__':
	main()