
import os
import os.path
import requests
import json

import time

from watchdog.events import FileSystemEventHandler
from pathlib import Path



from __init__ import URL_API


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

		if os.path.exists(event.src_path):

			url = URL_API + str(path).replace('\\','/')


			'''
			Comprobar si el archivo ya existe en el server para no volver a re-enviar
			'''


			url = url.replace('data','list')
			r = requests.get(url)


			if r.status_code == 404:


				if os.path.isfile(event.src_path):


					url = URL_API + str(path.parent).replace('\\','/')

					files = {'upload_file': open(event.src_path,'rb')}
					requests.post(url,files = files)


					self.message = {
						'status': "created",
						'path': str(path.parent).replace('\\','/'),
						'name': path.name,
					}



				elif os.path.isdir(event.src_path):
					#Es una carpeta
					url = URL_API + str(path).replace('\\','/')
					data = json.dumps({'path':event.src_path})
					requests.post(url,json=data)
					


			else:
				pass #Ya existe en el server
			


		else:
			#File no found
			pass



	def on_deleted(self,event):

		path = event.src_path.split(self.folder)
		path = 'data/files/' + path[1]
		path = Path(path)
		url = ''

		if os.path.exists:


			url = URL_API + str(path) 
			url = url.replace('\\','/')
			
			r = requests.delete(url)





		else:
			pass #Ya está borrado

		self.message = {
			'status': 'removed',
			'path': str(path.parent).replace('\\','/'),
			'name': path.name,
		}




	def on_modified(self,event):

		path = event.src_path.split(self.folder)
		path =  'data/files/' + path[1]
		path = Path(path)
		url = ''






		if os.path.isfile(event.src_path):



			'''
			para comprobar que solo ha cambiado el nombre, se comparará el tamanio y
			la ultima fecha de modificacion del contenido
			'''


			_size = os.path.getsize(event.src_path)
			_modifie_file = os.path.getmtime(event.src_path)

			
			url = URL_API + str(path)
			url = url.replace('\\','/')
			url = url.replace('data','list')
			r = requests.get(url)



			'''
			con el status del response se comprueba si el archivo ha sido 
			renombreado en el cliente o servidor 
			'''



			if r.status_code == 200:

				data = r.json() 

				if _modifie_file != data['modified time']:

					url = URL_API + path._str.replace('\\','/')
					_file = {'upload_file': open(event.src_path,'rb')}
					requests.put(url,files = _file)

					self.message = {
						'status': 'modified',
						'path': str(path.parent).replace('\\','/'),
						'name': path.name,
					}


				else:
					pass



			elif r.status_code == 404:

				url = URL_API + str(path.parent).replace('\\','/')
				url = url.replace('data','list')

				data = requests.get(url)
				files = data.json()
				files = files[str(path.parent).replace('\\','/')] #Accediendo a la lista de archivos de la ruta


				for _file in files:



					if _size == _file['size'] and _modifie_file == _file['modified time']:
						url = URL_API + _file['path'] + '/' + _file['name']
						data = json.dumps({'new name':path.name,'old name': _file['name']})

						self.message = {
							'status': 'renamed',
							'path': str(path.parent).replace('\\','/'),
							'name': path.name,
							'oldname':_file['name'],
						}
						
						requests.put(url,json = data)
						
						print(f'newname: {path.name}')
						print(f'oldname: {_file["name"]}')

						break


					else:
						pass

