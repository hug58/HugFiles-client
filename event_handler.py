
import os
import os.path
import requests
import json

import time

from watchdog.events import FileSystemEventHandler
from pathlib import Path


URL_API = 'http://127.0.0.1:5000/'



class EventHandler(FileSystemEventHandler):
	"""docstring for EventHandler"""


	folder = 'files'


	def __init__(self):
		self.message = {}


	def on_created(self,event):



		path = event.src_path.split(self.folder)
		path =  'data/files/' + path[1]
		path = Path(path)
		url = ''

		if os.path.isfile(event.src_path):


			url = URL_API + str(path.parent)
			url = url.replace('\\','/')

			files = {'upload_file': open(event.src_path,'rb')}
			requests.post(url,files = files)


		else:
			pass

		self.message = {
			'status': "created",
			'path': str(path.parent).replace('\\','/'),
			'name': path.name,
			'acces time': os.path.getatime(path),
			'modified time': os.path.getmtime(path),
		}



	def on_deleted(self,event):

		path = event.src_path.split(self.folder)
		path = 'data/files/' + path[1]
		path = Path(path)
		url = ''

		if os.path.isfile:

			url = URL_API + path._str 
			url = url.replace('\\','/')
			
			r = requests.delete(url)
			print(r.status_code)

		else:
			pass

		self.message = {
			'status': 'removed',
			'path': str(path.parent).replace('\\','/'),
			'name': path.name,
			'acces time': os.path.getatime(path),
			'modified time': os.path.getmtime(path),
		}




	def on_modified(self,event):

		path = event.src_path.split(self.folder)
		path =  'data/files/' + path[1]
		path = Path(path)
		url = ''


		if os.path.isfile(event.src_path):

			with open('data.json','r') as f:
				data = json.load(f)


				_size = os.path.getsize(path)
				_modifie_file = os.path.getmtime(path)


				files = data[str(path.parent).replace('\\','/')]

				if files and path.name in files:

					print("Solo ha cambiado el contenido c:")

					url = URL_API + path._str
					url = url.replace('\\','/')

					_file = {'upload_file': open(event.src_path,'rb')}
					requests.put(url,files = _file)


					self.message = {
						'status': 'modified',
						'path': str(path.parent).replace('\\','/'),
						'name': path.name,
						'acces time': os.path.getatime(path),
						'modified time': os.path.getmtime(path),
					}




				else:
					for keys in files.keys():
						_file = files[keys]

						if _size == _file['size'] and _modifie_file == _file['modified time']:

							url = URL_API + _file['path'] + '/' + _file['name']
							data = json.dumps({'new name': path.name, 'old name': _file['name']})
							requests.put(url,json = data)

							print(f'newname: {path.name}')
							print(f'oldname: {_file["name"]}')


							self.message = {
								'status': 'modified',
								'path': str(path.parent).replace('\\','/'),
								'name': path.name,
								'oldname': _file['name'],
								'acces time': _file['acces time'],
								'modified time': _file['modified time'],
							}



		else:
			pass #folders


