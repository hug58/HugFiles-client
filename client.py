
import asyncio
import websockets


import json
import os
import os.path
import requests

from watchdog.observers import Observer
from pathlib import Path

#Locals
from event_handler import EventHandler


from __init__ import URL_API,URL_WS


#Carpeta predeterminada (por el momento), la idea a futuro es que el usuario pueda configurar esto a su gusto
DEFAULT_FOLDER = "data/files/"


def _modified(filename,message):

	'''
	Si se dispara el evento "created" y "modified" puede generar errores
	'''


	try:
		_modifie_file = os.path.getmtime(filename)	
		
		if _modifie_file != message['modified time']:
			return True

		else:
			return False

	except:
		return True #de esta forma no hay que volver a modificar el archivo





def _created(message):

		
	if not os.path.isdir(message['path']):
		os.makedirs(message['path'],exist_ok=True)
		
	filename = message['path'] + '/' + message['name']

	_file_download(filename)	


	#Modificando las fechas mtime y atime en el archivo

	atime = message['acces time']
	mtime = message['modified time']

	os.utime(filename,(atime,mtime))


	print(f' save: {message["name"]}')


def _file_download(filename):

	'''
	Descargar y modificar la metada del archivo.
	'''

	url_file = URL_API +  filename

	with requests.get(url_file,stream= True) as r:
		r.raise_for_status()
		with open(filename,'wb') as f:
			for chunk in r.iter_content(1024):
				if chunk:
					f.write(chunk)




async def consumer_handler(websocket):


		async for message in websocket:

			_message = json.loads(message)


			filename = _message['path'] + '/' + _message['name']


			#Realizando cambios


			if  _message['status'] == 'created' or _message['status'] == 'done':
				

				try:
					if not os.path.exists(filename):
						_created(_message)
					else:
						if _modified(_message) :_created(_message)

				except:
					
					'''
					No es un string valido 
					'''					
					
					pass


			elif _message['status'] == 'modified':
				
				if _modified(filename,_message):
					_created(_message)

					print(f'modifcado {_message["name"]}')

				else: 
					print(f'modificado {_message["name"]} pero no ha cambiado, probablemente sea de otro cliente o reenviado del server')


			elif _message['status'] == 'renamed':

				if not os.path.exists(filename):
					
					oldname = f'{_message["path"]}/{_message["oldname"]}'

					os.rename(oldname,filename)
					print(f'{_message["oldname"]} ha sido cambiado a {_message["name"]}')
				else:
					pass

			elif _message['status'] == 'removed':
				

				if os.path.exists(filename):
					os.remove(filename)

				else:


					#Posiblemente fue borrado desde este cliente
					

					print(f'borrado {filename}')




async def producer_handler(websocket):
	
	event_handler = EventHandler()
	observer = Observer()
	observer.schedule(event_handler, path=DEFAULT_FOLDER, recursive=True)
	observer.start()
		
	while True:

		if event_handler.message != {}:

			#enviando msg al server

			_message = event_handler.message
			await websocket.send(json.dumps(_message))
			print(f'Sending... \n {_message} \n ')
			event_handler.message = {}

		else:

			#Sino esperar 1 seg

			await asyncio.sleep(1)


async def main():


	#Generando la carpeta predeterminada sino existe


	if not os.path.isdir(DEFAULT_FOLDER):
		os.makedirs(DEFAULT_FOLDER,exist_ok=True)



	#Conectando al servidor websocket


	async with websockets.connect(URL_WS) as websocket:


		''' 
		Ejecutando 2 tareas en paralelo:
			
			consumer_handler() guarda y efectua los cambios en los archivos

			producer_handler() envia los cambios al servidor para replicar el msg a los demás clientes

		'''
	
		consumer_task = asyncio.create_task(
			consumer_handler(websocket)
			)


		producer_task = asyncio.create_task(
			producer_handler(websocket)
			)

		await consumer_task
		await producer_task

				

asyncio.run(main())
#asyncio.get_event_loop().run_until_complete(main())
