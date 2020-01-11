
import os
import os.path
import requests
import json

import time

from watchdog.events import FileSystemEventHandler
from pathlib import Path


URL_API = 'http://127.0.0.1:5000/api/'



class EventHandler(FileSystemEventHandler):
	"""docstring for EventHandler"""


	foulder = 'files'


	def __init__(self):
		pass

	def on_created(self,event):



		path = event.src_path.split(self.foulder)
		path =  'data/files/' + path[1]
		path = Path(path)


		if os.path.isfile(event.src_path):

			url = URL_API + path._srt 
			url = url.replace('\\','/')

			files = {'upload_file': open(event.src_path,'rb')}
			requests.post(url,files = files)


		else:
			pass




	def on_deleted(self,event):

		path = event.src_path.split(self.foulder)
		path = 'data/files/' + path[1]
		path = Path(path)


		if os.path.isfile:

			url = URL_API + path._srt 
			url = url.replace('\\','/')
			
			r = requests.delete(url)
			print(r.status_code)

		else:
			pass



	def on_modified(self,event):

		path = event.src_path.split(self.foulder)
		path =  'data/files/' + path[1]
		path = Path(path)



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


				else:
					for keys in files.keys():
						_file = files[keys]

						if _size == _file['Size'] and _modifie_file == _file['Modified time']:

							url = URL_API + _file['Path'] + '/' + _file['Name']
							data = json.dumps({'New name': path.name, 'Old name': _file['Name']})
							requests.put(url,json = data)

							print(f'newname: {path.name}')
							print(f'oldname: {_file["Name"]}')


		else:
			pass #Foulders

