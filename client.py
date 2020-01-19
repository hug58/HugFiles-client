
import asyncio
import websockets


import json
import os
import os.path
import requests

from watchdog.observers import Observer
from pathlib import Path

#Locals
from event_handler import EventHandler,URL_API




DEFAULT_FOLDER = "data/files/"


def _created(file):

		
	if not os.path.isdir(file['path']):
		os.makedirs(file['path'],exist_ok=True)
		
	filename = file['path'] + '/' + file['name']

	_file_download(filename)	

	atime = file['acces time']
	mtime = file['modified time']

	os.utime(filename,(atime,mtime))

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

		files = {}
		directory = {}
		path = ''
		

		async for message in websocket:

			_message = json.loads(message)

			print(_message)


			if _message['status'] == 'done':

				if path == _message['path'] or path == '':
					files[_message['name']] = _message
				else:
					directory[path] = files
					files = {}

					#Cambiando de directorio
					
					files[_message['name']] = _message
					directory[_message['path']] = files

				path = _message['path']
				filename = _message['path'] + '/' + _message['name']


				'''
				Para no descargar el archivo otra vez
				'''





				if not os.path.exists(filename):
					_created(_message)

				with open('data.json','w+') as f:
					json.dump(directory,f)


			elif _message['status'] == 'removed':
				pass


			elif _message['status'] == 'modified':
				pass


			elif _message['status'] == 'created':

				if not os.path.exists(filename):
					_created(_message)

				_created(_message)





async def producer_handler(websocket):
	
	event_handler = EventHandler()
	observer = Observer()
	observer.schedule(event_handler, path=DEFAULT_FOLDER, recursive=True)
	observer.start()
		
	while True:

		if event_handler.message != {}:
			_message = event_handler.message
			await websocket.send(json.dumps(_message))
			print(f'Sending... \n \n{_message} \n \n ')
			event_handler.message = {}
		else:
			await asyncio.sleep(1)

	#await asyncio.sleep(1)


async def main():

	url = "ws://localhost:7000"

	if not os.path.isdir(DEFAULT_FOLDER):
		os.makedirs(DEFAULT_FOLDER,exist_ok=True)


	async with websockets.connect(url) as websocket:

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
