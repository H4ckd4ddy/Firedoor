import docker
import json
from config_database import database

class docker_manager():
	
	data = {}
	
	@classmethod
	def web_entrypoint(cls, client_ip, get, post):
		if len(get) > 0:
			if get[0] == 'containers':
				if len(get) == 3:
					return 200, cls.manage_container(get[1], get[2])
				else:
					return 200, json.dumps(cls.get_containers_list())
		else:
			return cls.return_interface()
	
	@classmethod
	def get_containers_list(cls):
		client = docker.from_env()
		result = []
		try:
			client.ping()
		except:
			container_infos = {}
			container_infos['short_id'] = ''
			container_infos['id'] = ''
			container_infos['name'] = 'Unable to reach Docker'
			container_infos['status'] = 'error'
			container_infos['image'] = ''
			result.append(container_infos)
		else:
			containers_list = client.containers.list(True)
			for container_object in containers_list:
				container = client.containers.get(container_object.id)
				container_infos = {}
				container_infos['short_id'] = container.short_id
				container_infos['id'] = container.id
				container_infos['name'] = container.name
				container_infos['status'] = container.status
				container_infos['image'] = container.attrs['Config']['Image']
				result.append(container_infos)
		return result
	
	@classmethod
	def manage_container(cls, container_id, action):
		client = docker.from_env()
		result = {}
		try:
			client.ping()
		except:
			result['status'] = 'error'
			result['msg'] = 'Unable to reach docker'
		else:
			try:
				container = client.containers.get(container_id)
			except:
				result['status'] = 'error'
				result['msg'] = 'Non-existent container'
			else:
				try:
					if action == 'stop':
						container.stop()
					elif action == 'start':
						if container.status == 'paused':
							container.unpause()
						else:
							container.start()
					elif action == 'pause':
						container.pause()
				except:
					result['status'] = 'error'
					result['msg'] = 'Unable to perfom action on container'
				else:
					result['status'] = 'ok'
					result['msg'] = 'Action performed'
			
		return json.dumps(result)
	
	@classmethod
	def return_interface(cls):
		with open('interface.html', 'r') as interface:
			html = interface.read()
			return 200, html