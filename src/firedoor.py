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
from installer import *
from config_database import database
from firedoor_modules_manager import *
from request_handler import request_handler

version = 4.0

# GLOBAL INIT BEGIN
config_directory = "/etc/firedoor/"
# GLOBAL INIT END

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
	if len(sys.argv) > 1:
		if sys.argv[1] == 'install':
			installer.install(config_directory)
		elif sys.argv[1] == 'uninstall':
			installer.uninstall(config_directory)
		elif installer.check_installation(config_directory):
			installer.initialisation(config_directory)
			modules_manager.run_cli_module(sys.argv[1], sys.argv[2:])
		else:
			print('Firedoor is not correctly installed')
			exit()
	elif installer.check_installation(config_directory):
		installer.initialisation(config_directory)
		modules_manager.startup_modules()
		start_server()
	else:
		print('Firedoor is not correctly installed')
		exit()

if __name__ == '__main__':
	main()